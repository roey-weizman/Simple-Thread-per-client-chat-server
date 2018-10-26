import datetime,socket,logging
import threading
from Queue import Queue
from Packet import *
from threading import *
from clientHandler import ClientHandler


terminated=False

'''Printing Formatting issues'''
Fail = '\033[91m'
ENDC = '\033[0m'
WARNING = '\033[93m'
OKGREEN = '\033[92m'
BOLD = "\033[1m"
OKBLUE = '\033[94m'

'''Processing clients messages class'''
class Processor(object):
    def __init__(self,prefix,users,logger):
        self.prefix=prefix
        self.ackTime=str(datetime.datetime.now().time())
        self.clientHandler=ClientHandler(users)
        self.logger=logger

    def terminated(self):
        return self.isTerminated

    def getType(self,message):
        return unpack_from('B',message,8)[0]

    ''' Main method- processing the data, given connection established with the user'''
    def process(self,data,connection):
        """

        :param data:
        :param connection:
        :return:
        """

        current_sender,msg_type,bodyLen= connection,self.getType(data),unpack_from('>i',data,9)[0]

        if self.checkForAuthCode(data) is not 0:
             self.send_to_user(current_sender,NotAuthorizedErrorPacket().build_packet())
             return


        ''' GOT KEEP-ALIVE PACKET'''
        if msg_type==0x00:
            self.logger.info("Got from client Keep Alive Packet")
            self.clientHandler.handle_keep_alive(current_sender)

            ''' GOT CONNECT PACKET'''
        elif msg_type== 0x01:
            self.logger.info("Got from client CONNECT Packet")
            self.clientHandler.handle_connect(current_sender,bodyLen,data)

            ''' GOT DISCONNECT PACKET'''
        elif msg_type==0x02:
            self.logger.info("Got from client DISCONNECT Packet")
            self.clientHandler.handle_disconnect(current_sender)

            ''' GOT PUBLIC MESSAGE PACKET'''
        elif msg_type == 0x03:
            self.logger.info("Got from client PUBLIC MESSAGE Packet")
            self.clientHandler.handle_public(current_sender,bodyLen,data)

            ''' GOT PRIVATE MESSAGE PACKET'''
        elif msg_type == 0x04:
            self.logger.info("Got from client PRIVATE MESSAGE Packet")
            self.clientHandler.handle_private(current_sender,bodyLen,data)

            ''' GOT SUDDEN DISCONNECT PACKET'''
        elif msg_type==0x05:
            self.logger.info("Got from client SUDDEN DISCONNECT Packet")
            self.clientHandler.handle_SuddenDiscconnect(current_sender)

            ''' GOT UNIDENTIFIED PACKET'''
        else:
            self.logger.info("Got from client UNIDENTIFIED Packet")
            self.clientHandler.handle_unidentified(current_sender)



    ''' Checks weather given message is formatted according to protocol'''
    def checkForAuthCode(self,authBuffer):
        msCode=unpack_from('B'*8, authBuffer,0)
        return cmp(msCode,self.prefix)


'''Main Server class'''
class Server(object):

    def __init__(self):
        self.localHost='127.0.0.1'
        self.port=15672
        self.logger = logging.getLogger("my-logger")
        self.sock=self.socket_connection()
        self.bufferSize=2<<10
        self.prefix=(0xDE, 0xAD, 0xBE, 0xEF, 0xBE, 0xEF, 0xDE, 0xAD)
        self.users = dict()
        self.thread_lock = Lock()
        self.serverQ=Queue(maxsize=0)



    '''Establishing a non-blocking socket connection'''
    def socket_connection(self):
        self.logger.info("Creating a socket")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger.info("Binding the socket to %s , listening in port %d", self.localHost, self.port)
        sock.bind((self.localHost, self.port))
        sock.setblocking(0)
        return sock



    '''Main-thread Serving Method'''
    def serve(self):

        print_begining()
        self.set_logger()
        self.sock.listen(5)
        '''Task's Queue Thread'''
        threading.Thread(target=self.handle_requests, args=()).start()

        while True:
            try:
                connection, address = self.sock.accept()
                '''Thread Per Connection Thread'''
                threading.Thread(target=self.listenToClient, args=(connection,address)).start()
            except:
                continue




    '''Producer Side Method'''
    def handle_requests(self):

        processor = Processor(self.prefix, self.users,self.logger)
        while True and not terminated:
            # Get the task from the work queue
            while not self.serverQ.empty() and not terminated:
                self.logger.info("Server started processing data from Client")
                item =self.serverQ.get()
                processor.process(item['data'],item['conn'])
                self.serverQ.task_done()
                self.logger.info("Server finished processing data from Client")



    '''Serving a Specific Client Method'''
    def listenToClient(self, connection,address):

        print OKBLUE +'start to serve a client' +ENDC+'\n'
        self.logger.info("Server isServing new client")

        while True and not terminated:
            try:
                data = connection.recv(self.bufferSize)
                if data:
                    self.logger.info("Server got new Data from Client")
                    item = {'data': data, 'conn': connection}
                    self.serverQ.put(item)
                else:
                    self.logger.info("Client with connection %s Disconnected from service" % connection)
                    raise error('Client disconnected')
            except Exception as ex:
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    #non blocking IO exception- handled by iterating and waiting for the customer a specific time

                    if ex.args[0]==10035:
                        continue
                    elif ex.args[0]==10054:
                        self.logger.debug(message)
                        self.serverQ.put({'data':SuddenDiscconnectPacket().build_packet(),'conn':connection})
                        return
                    else:

                        connection.close()
                        return False
        connection.close()

    '''Logger Setup'''
    def set_logger(self):
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s - %(message)s]')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

def main():
    Server().serve()

def print_begining():
    print '======================================================'
    print('=========' + OKGREEN + "'Roey\'s Server is Starting to Serve'" + ENDC + '=========')
    print '======================================================\n'




if __name__ == '__main__':
    main()