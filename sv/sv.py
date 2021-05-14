import paho.mqtt.client as mqtt
import json

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883)

stringBase = "fse2020/170062465/"

def on_connect(client, userdata, flags, rc):
    print("connected to broker")
    client.subscribe('fse2020/170062465/dispositivos/#')
    # client.subscribe('fse2020/170062465/estado')
    
def on_message(client, userdata, message):
    print(message.topic)
    topic = message.topic
    if("fse2020/170062465/dispositivos/" in (topic)):
        print(json.loads(message.payload.decode())['id'])
        id = json.loads(message.payload.decode())['id']
        print("Vamos cadastrar jaja {id}".format(id=id))
        comodo = input('Onde você gostaria de cadastra-lo?')
        obj={}
        obj['comodo']=comodo
        jsonComodo = json.dumps(obj)
        client.unsubscribe('fse2020/170062465/dispositivos/#')
        client.publish(topic, jsonComodo)
        client.subscribe('fse2020/170062465/dispositivos/#')


while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()