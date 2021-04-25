import socketserver
from socket import *
import re

address_port = ("localhost", 17002)


def send_mail(from_address, from_port, to_address, to_port, msg):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(3)

    try:
        clientSocket.connect((to_address, to_port))
    except Exception as e:
        return (False, "Fail to connect BE Server: {}.".format(e))

    recv = clientSocket.recv(1024).decode()
    if recv[:3] != '220':
        clientSocket.close()
        return (False, "Fail to connect BE Server.")

    heloCommand = "HELO AU\r\n"
    clientSocket.send(heloCommand.encode())
    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        clientSocket.close()
        return (False, "HELO Failed: {}.".format(e))
    if recv[:3] != '250':
        clientSocket.close()
        return (False, "HELO Failed.")

    print("HERE")
    fromCommand = 'MAIL FROM: <{}:{}>\r\n'.format(from_address, from_port)
    clientSocket.sendall(fromCommand.encode())
    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        clientSocket.close()
        return (False, 'MAIL FROM Failed: {}.'.format(e))
    if recv[:3] != '250':
        clientSocket.close()
        return (False, 'MAIL FROM Failed.')

    toCommand = 'RCPT TO: <{}:{}>\r\n'.format(to_address, to_port)
    clientSocket.sendall(toCommand.encode())
    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        clientSocket.close()
        return (False, 'RCPT TO Failed: {}.'.format(e))

    if recv[:3] != '250':
        clientSocket.close()
        return (False, 'RCPT TO Failed.')

    dataCommand = 'DATA\r\n'
    clientSocket.sendall(dataCommand.encode())
    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        clientSocket.close()
        return (False, 'DATA Failed: {}.'.format(e))

    if recv[:3] != '250':
        clientSocket.close()
        return (False, 'DATA Failed.')

    clientSocket.sendall(msg.encode())
    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        clientSocket.close()
        return (False, 'SENDING MESSAGE Failed: {}.'.format(e))
    if recv[:3] != '250':
        clientSocket.close()
        return (False, 'SENDING MESSAGE Failed.')

    clientSocket.close()
    return (True, "Success.")


class emailServer(socketserver.BaseRequestHandler):
    def handle(self):
        print("Connection: from {}".format(self.client_address))
        self.request.send("220".encode())

        msg_from = ""
        msg_to_address = ""
        msg_to_port = 0
        msg_body = ""

        while True:
            try:
                data = self.request.recv(1024).decode()
                if data[:4] == "HELO":
                    self.request.send("250 Mail OK".encode())
                elif data[:9] == "MAIL FROM":
                    p = re.compile(r"[<](.*)[>]", re.S)
                    msg_from_address, msg_from_port = re.findall(p, data)[
                        0].split(':')
                    msg_from_port = int(msg_from_port)
                    self.request.send("250 Mail OK".encode())
                elif data[:7] == "RCPT TO":
                    p = re.compile(r"[<](.*)[>]", re.S)
                    msg_to_address, msg_to_port = re.findall(p, data)[
                        0].split(':')
                    msg_to_port = int(msg_to_port)
                    print("Sending to", msg_to_address, msg_to_port)
                    self.request.send("250 Mail OK".encode())
                elif data[:4] == "DATA":
                    print("Start data transmission.")
                    self.request.send("250 Mail OK".encode())
                    msg_body = self.request.recv(1024).decode()
                    print("Message:", msg_body)

                    status, error = send_mail(
                        msg_from_address, msg_from_port, msg_to_address, msg_to_port, msg_body)
                    print(status, error)

                    if status == False:
                        self.request.send("FAILURE: {}".format(error))
                    else:
                        self.request.send("250 Mail OK".encode())
                    break
            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    s = socketserver.ThreadingTCPServer(address_port, emailServer)
    s.serve_forever()
