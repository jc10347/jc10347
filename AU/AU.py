from flask import Flask, request
from urllib.parse import urlparse

from socket import *


def send_mail(from_address, from_port, to_address, to_port, msg):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.settimeout(3)

    try:
        clientSocket.connect((from_address, from_port))
    except Exception as e:
        return (False, "Fail to connect AE Server: {}.".format(e))

    recv = clientSocket.recv(1024).decode()
    if recv[:3] != '220':
        clientSocket.close()
        return (False, "Fail to connect AE Server.")

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


app = Flask(__name__)


def parse_url(str):
    _url = urlparse("http://" + str)
    return _url.hostname, _url.port


def do_sending(msg_from, msg_to, msg_body):
    from_address, from_port = parse_url(msg_from)
    to_address, to_port = parse_url(msg_to)
    status, error = send_mail(from_address, from_port,
                              to_address, to_port, msg_body)
    if status == False:
        return ("FAILURE: {}".format(error))
    else:
        return "SUCCESS: Message sent successfully."


@app.route('/email', methods=["GET"])
def get_message():
    message_from = request.args.get("from")
    message_to = request.args.get("to")
    message_body = request.args.get("message")
    print(message_from, message_to, message_body)
    if message_from == None or message_to == None or message_body == None:
        return ("<h1>400 Error</h1> Missing or wrong arguments.", 400)
    return do_sending(message_from, message_to, message_body)


if __name__ == "__main__":
    app.run(port=17001, host="0.0.0.0")
