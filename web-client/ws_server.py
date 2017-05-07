import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import socket
import json
#import ros

from pprint import pprint
'''
This is a simple Websocket Echo server that uses the Tornado websocket handler.
Please run `pip install tornado` with python of version 2.7.9 or greater to install tornado.
This program will echo back the reverse of whatever it recieves.
Messages are output to the terminal for debuggin purposes. 
''' 


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('new connection')
      
    def on_message(self, message):
        # print('message received:  {}'.format(message))
        data = json.dumps(message)
        pprint(data)
        left = []

        # Reverse Message and send it back
        # print ('sending back message: {}'.format( message[::-1]))
        # self.write_message(message[::-1])
 
    def on_close(self):
        print('connection closed')
 
    def check_origin(self, origin):
        return True
 
application = tornado.web.Application([
    (r'/ws', WSHandler),
])
 
 
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)
    myIP = socket.gethostbyname(socket.gethostname())
    print ('*** Websocket Server Started at {}***'.format(myIP))
    tornado.ioloop.IOLoop.instance().start()
