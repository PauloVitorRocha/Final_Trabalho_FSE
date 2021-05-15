from PyQt5 import QtWidgets
import paho.mqtt.client as mqtt
import json
import unidecode
# from PyQt5 import *
# from PyQt5.QtWidgets import QApplication, QMainWindow
# import sys



# class RAPAZ:
#     def window(self):
#         app = QApplication(sys.argv)
#         win = QMainWindow()
#         win.setGeometry(200, 200, 300, 300)
#         win.setWindowTitle("TITULO JANELA")
#         label = QtWidgets.QLabel(win)
#         label.setText("My label")
#         label.move(50, 50)
#         win.show()
#         sys.exit(app.exec_())

#     def comunicacaoMQTT(self):
        


# if __name__ == '__main__':
#     RAPAZ.window()

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883)

stringBase = "fse2020/170062465/"
espList = {}


def on_connect(client, userdata, flags, rc):
    print("connected to broker")
    client.subscribe('fse2020/170062465/dispositivos/#')
    # client.subscribe('fse2020/170062465/estado')
    
def on_message(client, userdata, message):
    # print(message.topic)
    topic = message.topic
    #se for cadastrar novo dispositivo
    if("fse2020/170062465/dispositivos/" not in (topic)):
        for key, value in espList.items():
            print("key = ",key)
            print("value = ",value)

    if("fse2020/170062465/dispositivos/" in (topic)):
        id = json.loads(message.payload.decode())['id']
        if(id in espList):
            print("ESP ja cadastrada")
        else:
            comodo = input('Onde você gostaria de cadastrar o novo equipamento?')
            comodo = unidecode.unidecode(comodo).replace(' ','').lower()
            msg={}
            msg['comodo']=comodo
            jsonComodo = json.dumps(msg)
            client.unsubscribe('fse2020/170062465/dispositivos/#')
            client.publish(topic, jsonComodo)
            novoTopico = stringBase+comodo + '/temperatura'
            espList[id] = novoTopico
            client.subscribe(novoTopico)


while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()