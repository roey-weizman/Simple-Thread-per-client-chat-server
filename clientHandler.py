import threading,time
from Packet import *


'''Printing Formatting issues'''
Fail = '\033[91m'
ENDC = '\033[0m'
WARNING = '\033[93m'
OKGREEN = '\033[92m'
BOLD = "\033[1m"
OKBLUE = '\033[94m'

'''Handling Client messages class'''
class ClientHandler(object):
    def __init__(self,users):
        self.users=users
        self.keep_alive_time=time.time()
        self.lock = threading.Lock()


    def handle_keep_alive(self,sender):
        if self.find_userName(sender) in self.users:
            seconds_since=int(time.time()-self.keep_alive_time)
            self.send_to_user(sender, KeepAliveAck(str(seconds_since)).build_packet())

        return None

    def handle_connect(self,sender,bodyLen, data):
        joined_name = ''.join(unpack_from('c' * bodyLen, data, 13))
        if joined_name in self.users:
            self.keep_alive_time = time.time()
            ErrorMessage = "Connection established before, no need to connect again!"
            self.send_to_user(sender, AlreadyRegisteredErrorPacket(ErrorMessage).build_packet())
        elif joined_name not in self.users and self.is_connected(sender):  # same connection
            ErrorMessage = "You are trying to connect with another username!"
            self.send_to_user(sender, NotAuthorizedErrorPacket(ErrorMessage).build_packet())
        else:
            self.add_user(joined_name, sender)
            self.keep_alive_time = time.time()
            existing_users = ",".join(list(self.users))
            self.send_to_user(sender, LoginAckPacket(existing_users).build_packet())
            self.broadcast(ClientJoinedPacket(joined_name).build_packet(), sender)
            return True

    def handle_disconnect(self,sender):
        if not self.is_connected(sender):
            ErrorMessage = "Cant send message from unconnected client, please connect!"
            self.send_to_user(sender, UnregisteredClientErrorPacket(ErrorMessage).build_packet())
        else:
            self.keep_alive_time = time.time()
            leaving_connection = sender
            leaving_name = self.find_userName(leaving_connection)
            self.remove_user(leaving_name)
            self.send_to_user(sender, GoodbyePacket().build_packet())
            terminated = True
            self.broadcast(ClientLeftPacket(leaving_name).build_packet(), sender)
            return False


    def handle_SuddenDiscconnect(self,sender):
        if not self.is_connected(sender):
            ErrorMessage = "Cant send message from unconnected client, please connect!"
            self.send_to_user(sender, UnregisteredClientErrorPacket(ErrorMessage).build_packet())
        else:
            self.keep_alive_time = time.time()
            leaving_connection = sender
            leaving_name = self.find_userName(leaving_connection)
            self.remove_user(leaving_name)
            self.broadcast(ClientLeftPacket(leaving_name).build_packet(), sender)
            return False

    def handle_public(self,sender,bodyLen,data):
        if not self.is_connected(sender):
            ErrorMessage = "Cant send message from unconnected client, please connect!"
            self.send_to_user(sender, UnregisteredClientErrorPacket(ErrorMessage).build_packet())
        else:
            self.keep_alive_time = time.time()
            total_message = (''.join(unpack_from('c' * bodyLen, data, 13))).split('\n')
            message_GUID = total_message[0]  # TODO: Do something with this
            user_of_sender = self.find_userName(sender)
            message = user_of_sender + '\n' + total_message[1]
            self.send_to_user(sender, MessageEnqueuedPacket(message_GUID).build_packet())
            self.broadcast(NewMessagePacket(message).build_packet(), sender)
            return None

    def handle_private(self,sender,bodyLen, data):
        total_message = (''.join(unpack_from('c' * bodyLen, data, 13))).split('\n')
        message_GUID = total_message[0]  # TODO: Do something with this
        user_to_send = total_message[1]
        message = total_message[2]
        if not self.is_connected(sender):
            ErrorMessage = "Cant send message from unconnected client, please connect!"
            self.send_to_user(sender, UnregisteredClientErrorPacket(ErrorMessage).build_packet())
        elif self.isAuthenticated(user_to_send) is False:
            self.keep_alive_time = time.time()
            ErrorMessage = "Message #" + message_GUID + " cannot be delivered to " + user_to_send + ", Client is NOT registered "
            self.send_to_user(sender, UnregisteredClientMessageErrorPacket(ErrorMessage).build_packet())
        else:
            self.keep_alive_time = time.time()
            sender_userName = self.find_userName(sender)
            msg_to_send = sender_userName + "\n" + message
            self.send_to_user(sender, MessageEnqueuedPacket(message_GUID).build_packet())
            self.send_to_user(self.users[user_to_send], NewMessagePacket(msg_to_send).build_packet())
        return None

    def handle_unidentified(self,sender):
        ErrorMessage = "Illegal Request"
        self.send_to_user(sender, UnclassifiedRequestPacket(ErrorMessage).build_packet())
        return None

    def broadcast(self,message,conn):
        for key in self.users:
            if self.users[key]==conn:
                continue
            else:
                self.send_to_user(self.users[key], message)


    def is_connected(self,connection):
        for key in self.users:
            if self.users[key] == connection:
                return True
        return False

    def send_to_user(self,user_connection,message):
        try:
            user_connection.send(message)
        except Exception as e:
            err = e.args[0]
            if err == 10054:
                print(Fail + "Something is WRONG with our services, please try to retry your connection...." + ENDC + '\n')
                return

    def remove_user(self,user):
        try:
            del self.users[user]
        except KeyError:
            pass

    def add_user(self,userName,userSocket):
        self.users[userName] = userSocket

    def find_userName(self,connection):
        for key in self.users:
            if self.users[key] == connection:
                return key
        return None

    def isAuthenticated(self,user):
        if user in self.users:
            return True
        return False

def main():
    pass



if __name__ == '__main__':
    main()