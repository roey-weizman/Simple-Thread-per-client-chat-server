# Simple-Thread-per-client-chat-server

Chat server and a chat client, utilizing Threading, TCP Sockets, handling of raw binary data and more.

The server and client communicate with messages. Each message a (binary) string with the following structure:   

1.First 8 bytes are always 0xDE, 0xAD, 0xBE, 0xEF, 0xBE, 0xEF, 0xDE, 0xAD  

2.Messages are encoded with a TYPE-LENGTH-BODY (TLB) scheme: A single byte for TYPE, 4 big-endian bytes for LENGTH, and LENGTH bytes for BODY). For simplicity, the body is always a string, even when the body is a number.  


Message Codes:

0x00 -Client Keep-alive. No body. 
0x01 -Client Connect. Body = <name of client> 
0x02 -Client Disconnect. Body = <name of client> 
0x03 -Client Public Message. Body = <message GUID>\n<message> 
0x04 -Client Private Message. Body = <message GUID>\n<target client>\n<message> 
0x10 -Server ACK for Client Keepalive. Body = String containing seconds since last KA received for this client.
0x11 -Server ACK for Client Connect. Body = String containing CSV of all available client names. 
0x12 -Server ACK for Message Enqueued. Body = <message GUID> 
0x13 -Server announcement of a party who has joined. Body = <client name> 
0x14 -Server announcement of a party who has left. Body = <client name> 
0x15 -Server announcement of a new message. Body = <sending client>\n<message> 
0x20 -Server Error – Received a message from an un-registered client 
0x21 -Server Error – Cannot deliver message to client X (unregistered) 
0x22 -Server Error – Cannot register client – already registered. 
0xEE -General Client Error. Body=Error description (stack trace?) 
0xFF -General Server Error. Body=Error description (stack trace?) 

  

 

 

 
