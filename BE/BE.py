import socketserver
from socket import *
import re
import json

address_port = ("localhost", 17003)

mail_list = []


def load_json():
    mails = []
    with open('mails.json', 'r') as f:
        mails = f.read()

    return mails


def save_json(mail_from, mail_to_address, mail_to_port, mail_msg):
    global mail_list
    mail = {
        "from": mail_from,
        "to_address": mail_to_address,
        "to_port": mail_to_port,
        "msg": mail_msg
    }
    mail_list.append(mail)
    ml = json.dumps(mail_list)
    with open("mails.json", 'w') as f:
        f.write(ml)


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
                    msg_from = re.findall(p, data)[0]
                    print("Sending from", msg_from)
                    self.request.send("250 Mail OK".encode())
                elif data[:7] == "RCPT TO":
                    p = re.compile(r"[<](.*)[>]", re.S)
                    msg_to_address, msg_to_port = re.findall(p, data)[
                        0].split(':')
                    print("Sending to", msg_to_address, msg_to_port)
                    self.request.send("250 Mail OK".encode())
                elif data[:4] == "DATA":
                    print("Start data transmission.")
                    self.request.send("250 Mail OK".encode())
                    msg_body = self.request.recv(1024).decode()
                    print("Message:", msg_body)

                    try:
                        save_json(mail_from=msg_from, mail_to_address=msg_to_address,
                                  mail_to_port=msg_to_port, mail_msg=msg_body)
                    except:
                        self.request.send("500 External Error".encode())
                    self.request.send("250 Mail OK".encode())
                    break
                elif data[:4] == "LIST":
                    mails = load_json()
                    self.request.send(mails.encode())
                    break

            except Exception as e:
                print(e)
                break


if __name__ == "__main__":
    s = socketserver.ThreadingTCPServer(address_port, emailServer)
    s.serve_forever()
