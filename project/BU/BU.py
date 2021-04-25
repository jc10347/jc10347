from flask import Flask, request
from socket import *
from urllib.parse import urlparse
import json

app = Flask(__name__)


def parse_url(str):
    _url = urlparse("http://" + str)
    return _url.hostname, _url.port


def get_email_list(s_addr, s_port):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    # clientSocket.settimeout(3)

    try:
        clientSocket.connect((s_addr, s_port))
    except Exception as e:
        return (False, "Fail to connect to BE server: {}".format(e))

    try:
        recv = clientSocket.recv(1024).decode()
    except Exception as e:
        return (False, "Fail to get Response: {}.".format(e))
    if recv[:3] != '220':
        clientSocket.close()
        return (False, "Fail to get Response.")

    clientSocket.send("LIST".encode())
    recv_all = ""
    try:
        recv = clientSocket.recv(1024).decode()
        recv_all += recv
        while len(recv) > 0:
            recv = clientSocket.recv(1024).decode()
            recv_all += recv
    except Exception as e:
        return(False, "No Response: {}".format(e))

    res = json.loads(recv_all)
    clientSocket.close()
    return (True, res)


@app.route('/email', methods=["GET"])
def get_email():
    server_address, server_port = parse_url(request.args.get("from"))
    print(server_address, server_port)
    status, result = get_email_list(server_address, server_port)
    if status == False:
        return ("FAILURE: {}".format(result))
    else:
        tbl = "<table border='1'><tr><td>From</td><td>Content</td></tr>"
        for mail in result:
            fr = mail["from"]
            bdy = mail["msg"]
            tbl += "<tr><td>{}</td><td>{}</td></tr>".format(fr, bdy)
        tbl += "</table>"
        # print(tbl)
        return ("SUCCESS. <br> <p>{}</p>".format(tbl))


if __name__ == "__main__":
    app.run(port=17004, host="0.0.0.0")
