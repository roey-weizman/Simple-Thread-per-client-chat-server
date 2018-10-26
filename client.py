import socket,threading,uuid,time
from Queue import Queue
from Packet import *

'''Printing Formatting issues'''
Fail = '\033[91m'
ENDC = '\033[0m'
WARNING = '\033[93m'
OKGREEN = '\033[92m'
BOLD = "\033[1m"
OKBLUE = '\033[94m'


'''Processor class for Server responds'''
class ClientProcessor(object):


    def __init__(self, prefix):
        self.prefix = prefix


    def terminated(self):
        return self.isTerminated



    def getType(self, message):
        return unpack_from('B', message, 8)[0]



    '''Main processing Method'''
    def process(self, data):

        bodyLen = unpack_from('>i', data, 9)[0]
        msg_type = self.getType(data)

        ''' GOT KEEP-ALIVE-ACK PACKET'''
        if type == 0x10:
            print "got ack for keep alive from server"+'\n'


            ''' GOT CONNECT-ACK PACKET'''
        elif msg_type == 0x11:
            self.got_message_from_server_printing()
            existing_users=(''.join(unpack_from('c' * bodyLen, data, 13))).split(',')
            self.print_existing_users(existing_users)
            return True

            ''' GOT MESSAGE-ENQUEUED PACKET'''
        elif msg_type == 0x12:
            self.got_message_from_server_printing()
            msg_GUID = (''.join(unpack_from('c' * bodyLen, data, 13)))
            print(OKBLUE + "Acknowledgment : Message #"+msg_GUID+ " is being processed" + ENDC+'\n')
            return None

            ''' GOT CLIENT-JOINED MESSAGE PACKET'''
        elif msg_type == 0x13:
             self.got_message_from_server_printing()
             joined_client=(''.join(unpack_from('c' * bodyLen, data, 13)))
             print(OKBLUE + joined_client+ " is online!" + ENDC+'\n')
             return None

             ''' GOT CLIENT-LEFT PACKET'''
        elif msg_type == 0x14:
            self.got_message_from_server_printing()
            left_client = ''.join(unpack_from('c' * bodyLen, data, 13))
            print(Fail + left_client + " has left the chat" + ENDC+'\n')
            return None

            ''' GOT NEW MESSAGE PACKET'''
        elif msg_type == 0x15:
            msg=(''.join(unpack_from('c' * bodyLen, data, 13))).split('\n')
            sender,msg=msg[0],msg[1]
            self.got_message_from_client_printing(sender,msg)
            return None

            ''' GOT GOODBYE PACKET'''
        elif msg_type == 0x09:
            self.got_message_from_server_printing()
            print(WARNING + "You have disconnected from the chat" + ENDC+'\n')
            return False

            ''' GOT UNREGISTERED PACKET, RECEIVER-UNREGISTERED , ALREADY REGISTERED, UNAUTHORIZED, UNIDENTIFIED PACKET'''
        elif msg_type == 0x20 or msg_type == 0x21 or msg_type == 0x22 or msg_type == 0xEE or msg_type == 0xFF:
            self.got_message_from_server_printing()
            Errormsg = (''.join(unpack_from('c' * bodyLen, data, 13))).split('\n')
            print(Fail + Errormsg[0] + ENDC+'\n')
            return None


    '''Printing Formatting'''
    def got_message_from_server_printing(self):
        print
        print '*******************************************************'
        print '*******************************************************'
        print '**         GOT A MESSAGE FROM THE SERVER            ***'
        print '*******************************************************'
        print '*******************************************************'
        print

    def got_message_from_client_printing(self,sender,msg):
        print
        print '*******************************************************'
        print '*******************************************************'
        print (OKBLUE +'      GOT A MESSAGE FROM  '+sender+':               ' + ENDC)
        print "Message: "
        print msg
        print '*******************************************************'
        print '*******************************************************'
        print

    '''Iterate and print existing users according to Server message'''
    def print_existing_users(self,users):
        i=1
        print(OKGREEN + "Welcome, Users alive in the chat:" + ENDC)
        for user in users:
            print "%d. %s" % (i, user)
            i+=1
        print


'''Main Client Class'''
class Client(object):


    def __init__(self,localHost,port):
        self.localHost = localHost
        self.port = port
        self.bufferSize=2<<10
        self.prefix=[0xDE, 0xAD, 0xBE, 0xEF, 0xBE, 0xEF, 0xDE, 0xAD]
        self.responses=Queue(maxsize=0)
        self.connected=False
        self.keep_alive_seconds=300 ## 5 MINUTES KEEP ALIVE
        self.last_keep_alive=time.time()



    '''Main Client connections to Server method'''
    def connect_to_server(self,s):
        try:
            s.connect((self.localHost, self.port))
        except Exception as e:
            err = e.args[0]
            if err == 10054 or err == 10061:
                print(Fail + "Something is with our services, please try to retry your connection...." + ENDC + '\n')
                return

        self.last_keep_alive=time.time()
        threading.Thread(target=self.request_producer, args=(s,)).start()
        threading.Thread(target=self.response_consumer, args=(s,)).start()
        threading.Thread(target=self.keep_alive_checker, args=(s,)).start()

        while True:
            command = raw_input('')
            print
            if isValid(command) is False:
                print(Fail + "Your command is not valid, please type again!" + ENDC+'\n')

                continue
            message = BuildMessage(command)
            try:
                s.send(message)
                self.last_keep_alive=time.time()
            except Exception as e:
                if e.args[0]==10054 or e.args[0]==10061:
                    print(Fail + "Something is WRONG with our services, please try to retry your connection...." + ENDC +'\n')
                    return

        print "You have left the chat.."
        s.close()



    '''Thread that responsible to enqueue Server response'''
    def request_producer(self,sock):
        while True:
            try:
                data = sock.recv(self.bufferSize)
                self.last_keep_alive=time.time()
            except Exception as e:
                err = e.args[0]
                if err == 10054:
                    print(Fail + "Something is WRONG with our services, please try to retry your connection...." + ENDC + '\n')
                    return
                continue
            self.responses.put(data)



    '''Thread the responsible to consume, process and present Server response'''
    def response_consumer(self,socket):
        processor = ClientProcessor(self.prefix)
        #keep_alive_thread=threading.Timer(10.0, self.keep_alive_sending,[socket])  # called every 5 minute
        while True:
            # Get the task from the work queue
            while not self.responses.empty():
                item = self.responses.get()
                connection_indicator=processor.process(item)
                self.set_keep_alive(connection_indicator)
                #self.keep_alive_schedueling(connection_indicator,keep_alive_thread)
                self.responses.task_done()




    '''setting keep alive sending according to user connectivity'''
    def set_keep_alive(self,indicator):
        if indicator is True:
            self.connected = True
            self.last_keep_alive=time.time()
        if indicator is False:
            self.connected = False



    '''calculate time in order to send Ack Package every self.keep_alive_seconds Seconds '''
    def keep_alive_checker(self,sock):
        while True:
            if time.time()-self.last_keep_alive >= self.keep_alive_seconds:
                print "sending ack package from client!"
                try:
                    sock.send(KeepAlivePacket().build_packet())
                except Exception as e:
                    if e.args[0] == 10054:
                        print(
                                    Fail + "Something is WRONG with our services, please try to retry your connection...." + ENDC + '\n')
                        return
                self.last_keep_alive = time.time()






def main():
    localHost, port = readDetailsFromFile()
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    myClient = Client(localHost, int(port))
    myClient.connect_to_server(mySocket)


'''Build the message from Shell-like User input'''
def BuildMessage(command):
     commandArr=command.split(' ')
     if commandArr[0] == 'CONNECT':
        return LoginPacket(commandArr[1]).build_packet()
     elif commandArr[0] == 'DISCONNECT':
         return DiscconnectPacket().build_packet()
     else:
         if commandArr[1]=='ALL':
             return PublicMessagePacket(uuid.uuid4().get_hex()+'\n'+get_msg_from_command(commandArr[2:])).build_packet()
         else:
             return PrivateMessagePacket(uuid.uuid4().get_hex()+'\n'+commandArr[1]+'\n'+get_msg_from_command(commandArr[2:])).build_packet()



'''message part Unpacking'''
def get_msg_from_command(arr):
    return ' '.join(arr)



'''Detail For connection resides in Configuration file'''
def readDetailsFromFile():
    f = open("Configuration File.txt")
    line=f.readline().split(",")
    return line[0],line[1]



'''Command Line Client Protocol'''
def isValid(command):
    commandArr=command.split(' ')
    if len(commandArr)<1:
        return False

    if commandArr[0]=='CONNECT':
        if len(commandArr) < 2 or len(commandArr) > 2:
            return False
        return True

    elif commandArr[0]=='DISCONNECT':
        if len(commandArr) > 1:
            return False
        return True

    elif commandArr[0]=='SEND':
        if len(commandArr) < 3 or not commandArr[1] or not commandArr[2]:
            return False
        return True
    else:
        return False



if __name__ == '__main__':
    main()