import paho.mqtt.client as mqtt
import json
import unidecode
import threading
import time
import _thread
import sys
import signal
import os


registerEspSemaphore = threading.Event()
mainMenuSemaphore = threading.Event()
espMenuSemaphore = threading.Event()
hasNewEsp = 0
opcao=0
contador_disp = 0
cliente = []

class mqtt_device:
    id = ''
    comodo = ''
    entrada = ''
    saida = ''
    statusIn = 0
    statusOut = 0
    temp = 0
    hmd = 0



for i in range(5):
    cliente.append(mqtt_device())

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883)


stringBase = "fse2020/170062465/"


def on_connect(client, userdata, flags, rc):
    print("connected to broker")
    client.subscribe('fse2020/170062465/dispositivos/#')


def searchID(id):
    for i in range(contador_disp):
            if(cliente[i].id == id):
                return i
    return -1

def on_message(client, userdata, message):
    global contador_disp
    global hasNewEsp


    id = json.loads(message.payload.decode())['id']
    if("fse2020/170062465/dispositivos/" in (message.topic)):
        isRegistered = searchID(id)
        if(isRegistered!=-1):
            print("Esp já cadastrada")
            time.sleep(1)
            mainMenuSemaphore.set()
            return

        hasNewEsp=1
        registerEspSemaphore.wait()
        if (contador_disp == 5):
            print("Número máx de esps atingido")
            mainMenuSemaphore.set()
            return

        comodo = input('escreva o comodo onde a esp será cadastrada\n')
        comodo = unidecode.unidecode(comodo).replace(' ', '').lower()
        isLP = input('Esp é Low Power?(0/1)\n')
        
        msg = {}
        msg['comodo'] = comodo
        msg['isLP'] = int(isLP)
        jsonComodo = json.dumps(msg)

        client.unsubscribe('fse2020/170062465/dispositivos/#')
        client.publish(message.topic, jsonComodo)
        cliente[contador_disp].id = id        
        client.subscribe('fse2020/170062465/'+comodo+'/#')
        client.subscribe('fse2020/170062465/dispositivos/#')
        hasNewEsp=0
        contador_disp += 1
        mainMenuSemaphore.set()
        registerEspSemaphore.clear()
    else:
        func = message.topic.split('/')[-1]
        result = searchID(id)
        if func == 'temperatura':
            temp = json.loads(message.payload.decode())['temperatura']
            cliente[result].temp = temp
        elif func == 'umidade':
            hmd = json.loads(message.payload.decode())['umidade']
            cliente[result].hmd = hmd
        elif func == 'estado':
            saida = json.loads(message.payload.decode())['saida']
            entrada = json.loads(message.payload.decode())['entrada']
            cliente[result].statusOut = saida
            cliente[result].statusIn = entrada

def menuEsps():
    global contador_disp
    global cliente
    while(1):
        espMenuSemaphore.wait()
        os.system('cls' if os.name == 'nt' else 'clear')
        print('''----------------- MENU -----------------
5- Ligar led
7- voltar\n
''')
        for i in range(contador_disp):
            print(f'############# ESP {i+1} ##############')
            print('Nome da esp = ',cliente[i].id)
            print('temperatura = ',cliente[i].temp)
            print('humidade = ',cliente[i].hmd)
            print('estadoBotao = ',cliente[i].statusIn)
            print('estadoLed = ',not cliente[i].statusOut)
            print('##################################\n')
        
        print("\nPressione CTRL+Z para ativar o input")
        time.sleep(.5)


def semaphoreKeeper():
    registerEspSemaphore.clear()
    espMenuSemaphore.clear()
    mainMenuSemaphore.set()

def ligarLed():
    global client
    global cliente
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(contador_disp):
        print(f'{i+1}-', cliente[i].id)
    inpt = input('Qual esp deseja ligar/desligar o led?\n')
    inpt = int(inpt)-1
    while (inpt > contador_disp or inpt<0):
        print('opcao inválida, tente novamente')
        inpt = input('Qual esp deseja ligar/desligar o led?\n')
    print("msg enviada para ")
    msg = {}
    msg['saida'] = 1
    msg = json.dumps(msg)
    print("msg = ", msg)
    topic = 'fse2020/170062465/dispositivos/' + cliente[inpt].id
    client.unsubscribe('fse2020/170062465/dispositivos/#')
    client.publish(topic, msg)
    client.subscribe('fse2020/170062465/dispositivos/#')
    espMenuSemaphore.set()


def inputzao():
    global opcao
    opcao = input('\ndigite a opcao desejada\n')
    if(opcao=='1'):
        registerEspSemaphore.set()
        mainMenuSemaphore.clear()
    elif(opcao=='2'):
        espMenuSemaphore.set()
    elif(opcao=='5'):
        espMenuSemaphore.clear()
        ligarLed()
    elif(opcao=='7'):
        espMenuSemaphore.clear()
        mainMenuSemaphore.set()
    else:
        print("opcao inválida, tente novamente")
        inputzao()
        
def signal_handler(sig, frame):
    
    mainMenuSemaphore.clear()
    if(espMenuSemaphore.is_set):
        espMenuSemaphore.clear()
    inputzao()


def close_threads(sig, frame):
    print("vamo fechar")
    for i in range(3):
        _thread.exit()
    

signal.signal(signal.SIGTSTP, signal_handler)
# signal.signal(signal.SIGINT, close_threads)

def menu():
    global hasNewEsp
    global opcao
    while(1):
        mainMenuSemaphore.wait()
        os.system('cls' if os.name == 'nt' else 'clear')
        if hasNewEsp:
            print('''----------------- MENU ----------------- 
# Nova esp para ser cadastrada, digite 1 para adicionar
1- add esp
2- info esp
3- sair''')
            print("\nPressione CTRL+Z para ativar o input")

        else:
            print('''----------------- MENU -----------------
1- add esp
2- info esp
3- sair''')
            print("\nPressione CTRL+Z para ativar o input")
        time.sleep(3)


t0 = threading.Thread(target=semaphoreKeeper).start()
t1 = threading.Thread(target=menu).start()
# t2 = threading.Thread(target=inputzao).start()
t3 = threading.Thread(target=menuEsps).start()

while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
