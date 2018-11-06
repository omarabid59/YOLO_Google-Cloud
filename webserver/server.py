import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid
from PIL import Image
import time

#from io import StringIO
from io import BytesIO
import uuid
import numpy
import json
from tornado.options import define, options
import tornado.httpserver
import sys
sys.path.append('../')
import opencv
import ssl

define("port", default=8888, help="run on the given poort", type=int)

class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
        (r"/", MainHandler),
        (r"/test", TestHandler),
        (r"/facedetector", FaceDetectHandler)
        ]

    settings = dict(
        cookie_secret="asdsafl.rleknknfkjqweonrkbknoijsdfckjnk 234jn",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False,
        autoescape=None,
        debug=True
        )
    tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("facedetect.html")
class TestHandler(tornado.web.RequestHandler):
  def get(self):
    self.render("facedetect.html")

class SocketHandler(tornado.websocket.WebSocketHandler):

  def open(self):
    logging.info('new connection')

  def on_message(self, message):
    image = Image.open(BytesIO(message))
    cv_image = numpy.array(image)
    self.process(cv_image)

  def on_close(self):
    logging.info('connection closed')

  def process(self, cv_image):
    pass

class FaceDetectHandler(SocketHandler):

  def process(self, cv_image):
    faces = opencv.detect_faces(cv_image)
    if len(faces) > 0:
      result = json.dumps(faces.tolist())
      self.write_message(result)



def main():
    tornado.options.parse_command_line()
    
    app = Application()
    ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_ctx.load_cert_chain("ssl/domain.crt",
                           "ssl/domain.key")

    
    http_server = tornado.httpserver.HTTPServer(app, ssl_options=ssl_ctx)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
  main()
