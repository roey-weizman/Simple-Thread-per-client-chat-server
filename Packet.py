import array
from struct import *

class Packet:
    def __init__(self,type,bodyLen,body):
       self.prefix=(0xDE, 0xAD, 0xBE, 0xEF, 0xBE, 0xEF, 0xDE, 0xAD)
       self.type=type
       self.bodyLen=bodyLen
       self.body=body


    """ RETURNING PACKED MESSAGE READY TO SEND"""
    def build_packet(self):

        prefixLen, typeLen, lengthLen= 8, 1, 4
        MSBuffer = array.array('B', '\0' * (prefixLen + typeLen + lengthLen + self.bodyLen))

        """Packing Buffer for prefix (for all kind of massages)"""
        pack_into('B' * 8, MSBuffer, 0, *self.prefix)
        """Packing Buffer for specific type """
        pack_into('B', MSBuffer, 8, self.type)
        """Packing Buffer for specific body length """
        pack_into('>i', MSBuffer, 9, self.bodyLen)
        """Packing Buffer for specific body """
        pack_into('c' * self.bodyLen, MSBuffer, 13, *list(self.body))

        return MSBuffer


class KeepAliveAck(Packet):
    def __init__(self,seconds_since):
        Packet.__init__(self,0x10,len(seconds_since),seconds_since)

class MessageEnqueuedPacket(Packet):
    def __init__(self,msg_GUID):
        Packet.__init__(self,0x12,len(msg_GUID),msg_GUID)

class GoodbyePacket(Packet):
    def __init__(self):
        Packet.__init__(self,0x09,0,"")

class KeepAlivePacket(Packet):
    def __init__(self):
        Packet.__init__(self,0x00,0,"")



class AlreadyRegisteredErrorPacket(Packet):
    def __init__(self,Error_message):
        Packet.__init__(self,0x22,len(Error_message),Error_message)



class ClientJoinedPacket(Packet):
    def __init__(self,name):
        Packet.__init__(self,0x13,len(name),name)

class UnclassifiedRequestPacket(Packet):
    def __init__(self,Error_message):
        Packet.__init__(self,0xFF,len(Error_message),Error_message)


class ClientLeftPacket(Packet):
    def __init__(self,name):
        Packet.__init__(self,0x14,len(name),name)



class DiscconnectPacket(Packet):
    def __init__(self):
        Packet.__init__(self,0x02,0,"")

class SuddenDiscconnectPacket(Packet):
    def __init__(self):
        Packet.__init__(self,0x05,0,"")


class LoginAckPacket(Packet):
    def __init__(self,users):
        Packet.__init__(self,0x11,len(users),users)



class NotAuthorizedErrorPacket(Packet):
    def __init__(self,Error_message):
        Packet.__init__(self,0xEE,len(Error_message),Error_message)



class NotRegisteredPacket(Packet):
    def __init__(self):
        Packet.__init__(self,0x20,0,"")


class LoginPacket(Packet):
    def __init__(self,name):
        Packet.__init__(self,0x01,len(name),name)



class NewMessagePacket(Packet):
    def __init__(self,nameAndMassage):
        Packet.__init__(self,0x15,len(nameAndMassage),nameAndMassage)



class PrivateMessagePacket(Packet):
    def __init__(self,GUID_name_message):
        Packet.__init__(self,0x04,len(GUID_name_message),GUID_name_message)



class UnregisteredClientMessageErrorPacket(Packet):
    def __init__(self,Error_message):
        Packet.__init__(self,0x21,len(Error_message),Error_message)


class PublicMessagePacket(Packet):
    def __init__(self,GUID_message):
        Packet.__init__(self,0x03,len(GUID_message),GUID_message)



class UnregisteredClientErrorPacket(Packet):
    def __init__(self,Error_message):
        Packet.__init__(self,0x20,len(Error_message),Error_message)



