from BaseHTTPServer import HTTPServer
from pysimplesoap.server import SoapDispatcher, SOAPHandler
import publisher_queue

# Create SOAP Dispatcher
dispatcher = SoapDispatcher(
    'my_dispatcher',
    location='http://localhost:8008/',
    action='http://localhost:8008/', #SOAPAction
    trace=False,
    ns=False)

subscriber_dictionary = {}
last_ids = {}

def publish(publisher_id, message):
    if message is not None:
        split_msg = message.split(':')
        msg_id = int(split_msg[0])
        content = str(split_msg[1])
    else:
        return ""

    print "\n GOT FROM PUBLISHER ", str(publisher_id), "==== MESSAGE:", message

    # if we get all messages in order
    if last_ids[publisher_id] + 1 == int(msg_id):
        pub_queue = publisher_queue[publisher_id]
        pub_queue.put_message(message)
        last_ids[publisher_id] = int(msg_id)
        return "OK"

    # repetition, ignore message
    elif last_ids[publisher_id] == int(msg_id):
        return "DUPLICATE"

    # notify that this message was not in order don't accept it
    else:
        return str(last_ids[publisher_id])

# register the user function
dispatcher.register_function('publish', publish,
    returns={'response': str},
    args={'publisher_id': int, 'message': str})

def main():
    print "Starting Server"
    httpd = HTTPServer(("", 8008), SOAPHandler)
    httpd.dispatcher = dispatcher
    httpd.serve_forever()

if __name__ == '__main__':
    main()