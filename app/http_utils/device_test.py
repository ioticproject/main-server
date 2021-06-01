from pubsub_client import PubSubClient

print("**********")
id_user = "5c19a5a2fcd64e2a9401225b61596b3d"
id_device = "85b4dbc8e1b44cd4b9a2e6aaeb26e851"
id_sensor = "42587716472441f08de9c8260fc280a5"

token = "36b5fe56debf4309a91817fba1efb743"
topic = id_user + '.' + id_device + '.' + id_sensor

client = PubSubClient(token)
import time
time.sleep(1)
client.publish(topic, {"id_sensor":id_sensor, "value":5})
