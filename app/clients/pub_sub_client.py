from websocket import create_connection
from websocket import WebSocketApp
import time
import json
import os

try:
    import thread
except ImportError:
    import _thread as thread

class PubSubAuth:
    ws = None

    def __init__(self, secret):
        self.ws = create_connection("ws://" + os.environ.get("PUB_SUB_HOST") + ":82")
        self.send("access-auth", {"secret": secret})
        self.check()
        pass


    def close(self):
        self.ws.close()

    def send(self, event, data):
        self.ws.send(json.dumps({ "event": event, "data": data}))
        print("sent " + event)

    def check(self):
        recv = str(self.ws.recv())
        if recv != "ack" :
            print("PubSubAuth error: " + recv)
            return recv

    def grantPublish(self, topic):
        self.send("grant-publish", topic)
        return self.check()

    def grantSubscribe(self, topic):
        self.send("grant-subscribe", topic)
        return self.check()

    def revokePublish(self, topic):
        self.send("revoke-publish", topic)
        return self.check()

    def revokeSubscribe(self, topic):
        self.send("revoke-subscribe", topic)
        return self.check()

    def revokeAll(self, token):
        self.send("revoke-all", token)
        return self.check()


class PubSubClient:
    ws = None
    token = None
    listener = None

    def __init__(self, token, listener=None):
        self.token = token
        self.listener = listener
        self.start()

    def start(self):
        def run(*args):
            print("### PubSubClient connecting ### ")
            self.ws = WebSocketApp("ws://" + os.environ.get("PUB_SUB_HOST") + ":81",
                                    on_message = self.on_message,
                                    on_error = self.on_error,
                                    on_close = self.on_close)
            self.ws.run_forever()
        thread.start_new_thread(run, ())
        time.sleep(1)
        self.subscribe("*")

    def send(self, event, data):
        self.ws.send(json.dumps({ "event": event, "data": data}))
        print("sent " + event)

    def on_message(self, ws, msg):
        msgObj = json.loads(msg)
        if msgObj["event"] == "error":
            print("Error: " + msgObj['data'])
            return

        print("message " + msg)
        # if self.listener:
        self.listener(msgObj["data"])

    def subscribe(self, pattern):
        self.send("subscribe", {"token": self.token, "pattern": pattern})

    def publish(self, pattern, data):
        self.send("publish", {"token": self.token,  "pattern": pattern, "data": data})

    def on_error(self, ws, error):
        print("### PubSubClient Error: ### " +  str(error))
        time.sleep(2)
        self.start()


    def on_close(self, ws):
        print("### PubSubClient Closed ###")
