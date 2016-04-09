from pysimplesoap.client import SoapClient
from pysimplesoap.server import SoapDispatcher, WSGISOAPHandler
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi
import logging


def echo(data):
    return '..%s..' % data


# Create SOAP Dispatcher
dispatcher = SoapDispatcher(
    'my_dispatcher',
    location='http://localhost:8888/',
    action='http://localhost:8888/', #SOAPAction
    namespace='http://example.com/simple.wsdl', prefix='ns0',
    trace=True,
    ns=True)

dispatcher.register_function('Echo', echo,
    returns={'resp': unicode}, args={'data': unicode})

def call_wsaa(input):
    # Create SOAP Client
    client = SoapClient

    # call the remote method
    try:
        results = client.loginCms(arg0=str(input))
    except:
        # save sent and received messages for debugging:
        open("request.xml", "w").write(client.xml_request)
        open("response.xml", "w").write(client.xml_response)
        raise

    # extract the result:
    ta = results['return'].encode("utf-8")
    return ta

def main():
    handler = WSGISOAPHandler(dispatcher)
    wsgi_app = tornado.wsgi.WSGIContainer(handler)
    tornado_app = tornado.web.Application(
       [
           ('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)),
       ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()