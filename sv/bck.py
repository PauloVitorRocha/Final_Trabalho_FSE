from PyQt5 import QtWidgets
import paho.mqtt.client as mqtt
import json
import unidecode
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys
import _thread
import time
import asyncio
import threading


class RAPAZ:

    stringBase = "fse2020/170062465/"
    espList = {}
    comodoList = []
    cliente = []
    shouldUpdate = 0

    def __init__(self):
        ...

    def menu(self):
        print('''
        Menuzao
        1 - add esp
        2 - check esp
        ''')
    # def window(self):
    #     app = QApplication(sys.argv)
    #     win = QMainWindow()
    #     win.setGeometry(200, 200, 300, 300)
    #     win.setWindowTitle("TITULO JANELA")
    #     label = QtWidgets.QLabel(win)
    #     for key, value in self.espList.items():
    #         label.setText(key)
    #         label.move(50, 50)
    #     win.show()
    #     sys.exit(app.exec_())

    def getList(self):
        for comodo in self.comodoList:
            print("No comodo {comodo}".format(comodo=comodo))

    # def checkMSG(self, message):
    #     topico = message.topic.split('/')[-2]
    #     self.getList()
    #     # print('Para o topico {topico} temos a msg:'.format(topico=topico))
    #     # print(message.payload.decode())

    #funcao roda ao conectar ao broker test.mosquito

    def on_connect(self, client, userdata, flags, rc):
        print("connected to broker")
        client.subscribe('fse2020/170062465/dispositivos/#')
        # client.subscribe('fse2020/170062465/estado')

    def on_message(self, client, userdata, message):
        # print(message.topic)
        topic = message.topic
        #se for ler dispositivo
        if("fse2020/170062465/dispositivos/" not in (topic)):
            # self.checkMSG(message)
            ...
            # for key, value in self.espList.items():
            #     print("key = ", key)
            #     print("value = ", value)

        if("fse2020/170062465/dispositivos/" in (topic)):
            idEsp = json.loads(message.payload.decode())['id']
            if(idEsp in self.espList):
                print("ESP ja cadastrada")
            else:
                self.cadastraEsp(client, topic, idEsp)

    def comunicacaoMQTT(self):
        while True:
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.loop_forever()

    def cadastraEsp(self, client, topic, idEsp):
        comodo = input(
            'Onde você gostaria de cadastrar o novo equipamento?')
        comodo = unidecode.unidecode(comodo).replace(' ', '').lower()
        msg = {}
        msg['comodo'] = comodo
        self.comodoList.append(comodo)
        jsonComodo = json.dumps(msg)
        client.unsubscribe('fse2020/170062465/dispositivos/#')
        client.publish(topic, jsonComodo)
        novoTopico = self.stringBase+comodo+'/#'
        self.espList[idEsp] = novoTopico
        client.subscribe(novoTopico)


def get_input():
    input("Press Enter to continue...")
    RAPAZ.cadastraEsp()


if __name__ == '__main__':
    clientes = []
    for i in range(5):
        clientes[i] = mqtt.Client()

    RAPAZ.client.connect("test.mosquitto.org", 1883)
    # x.window()
    # input_thread = threading.Thread(target=get_input)
    # input_thread.start()
    t2 = _thread.start_new_thread(x.comunicacaoMQTT, ())
    # t3 = _thread.start_new_thread(x.getList,())
    while True:
        ...

# while True:
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.loop_forever()
