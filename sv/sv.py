import paho.mqtt.client as mqtt
import json
import unidecode
import threading
import time
import sys
import signal
import os
from datetime import datetime
from pygame import mixer

registerEspSemaphore = threading.Event()
mainMenuSemaphore = threading.Event()
espMenuSemaphore = threading.Event()
hasNewEsp = 0
opcao=0
contador_disp = 0
cliente = []
svRunning = 1
alarme = 0
arquivo = ''

class mqtt_device:
    id = ''
    comodo = ''
    entrada = ''
    saida = ''
    statusIn = 0
    statusOut = 0
    temp = 0
    hmd = 0

#cria o vetor de devices
for i in range(5):
    cliente.append(mqtt_device())

#inicializa conexao mqtt
client = mqtt.Client()
client.connect("test.mosquitto.org", 1883)


def on_connect(client, userdata, flags, rc):
    print("connected to broker")
    client.subscribe('fse2020/170062465/dispositivos/#')

#procura no vetor de devices se ele existe
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
            return
        hasNewEsp=1
        registerEspSemaphore.wait()
        if (contador_disp == 5):
            print("Número máx de esps atingido")
            return
        comodo = input('escreva o comodo onde a esp será cadastrada\n')
        comodo = unidecode.unidecode(comodo).replace(' ', '').lower()        
        msg = {}
        msg['comodo'] = comodo
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
            if entrada != cliente[result].statusIn:
                escreveCSV(f'botão da esp {cliente[result].id} trocou de estado para estado {entrada}')
            cliente[result].statusOut = saida
            cliente[result].statusIn = entrada


def menuEsps():
    global contador_disp
    global cliente
    global svRunning
    while(svRunning):
        espMenuSemaphore.wait()
        os.system('cls' if os.name == 'nt' else 'clear')
        if hasNewEsp:
            print(f'''----------------- MENU -----------------
# Nova esp para ser cadastrada, volte para o menu principal para cadastrar
3- Alarme {alarme}
4- Ligar led
5- Apagar Esp
6- voltar\n
''')    
        else:
            print(f'''----------------- MENU -----------------
3- Alarme {alarme}
4- Ligar led
5- Apagar Esp
6- voltar\n
''')
        for i in range(contador_disp):
            print(f'############# ESP {i+1} ##############')
            print('Nome da esp = ',cliente[i].id)
            print('temperatura = ',cliente[i].temp)
            print('humidade = ',cliente[i].hmd)
            print('estadoBotao = ',cliente[i].statusIn)
            print('estadoLed = ',cliente[i].statusOut)
            print('##################################\n')
        print("\nPressione CTRL+Z para ativar o input")
        time.sleep(.5)


def resetarEsp():
    global client
    global cliente
    global contador_disp
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(contador_disp):
        print(f'{i+1}-', cliente[i].id)
    inpt = input('Qual esp deseja resetar?\n')
    inpt = int(inpt)-1
    while (inpt > contador_disp or inpt < 0):
        print('opcao inválida, tente novamente')
        inpt = input('Qual esp deseja resetar?\n')
        inpt = int(inpt)-1
    msg = {}
    msg['reset'] = 1
    msg = json.dumps(msg)
    topic = 'fse2020/170062465/dispositivos/' + cliente[inpt].id
    escreveCSV(f'A esp {cliente[inpt].id} foi resetada\n')
    cliente.pop(inpt)
    contador_disp-=1
    cliente.append(mqtt_device())
    client.unsubscribe('fse2020/170062465/dispositivos/#')
    client.publish(topic, msg)
    client.subscribe('fse2020/170062465/dispositivos/#')
    espMenuSemaphore.set()


def ligarLed():
    global client
    global cliente
    global arquivo
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(contador_disp):
        print(f'{i+1}-', cliente[i].id)
    inpt = input('Qual esp deseja ligar/desligar o led?\n')
    inpt = int(inpt)-1
    while (inpt > contador_disp or inpt<0):
        print('opcao inválida, tente novamente')
        inpt = input('Qual esp deseja ligar/desligar o led?\n')
        inpt = int(inpt)-1
    msg = {}
    msg['saida'] = int(not cliente[i].statusOut)
    cliente[i].statusOut = int(not cliente[i].statusOut)
    time.sleep(.1)
    msg = json.dumps(msg)
    topic = 'fse2020/170062465/dispositivos/' + cliente[inpt].id
    client.unsubscribe('fse2020/170062465/dispositivos/#')
    client.publish(topic, msg)
    client.subscribe('fse2020/170062465/dispositivos/#')
    escreveCSV(f'Led da esp {cliente[inpt].id} trocou de estado para {cliente[inpt].statusOut}')
    espMenuSemaphore.set()


#Trata CTRL+C
def close_threads(sig, frame):
    global svRunning
    global arquivo
    arquivo.close()
    print("\nEncerrando...\n")
    svRunning = 0
    sys.exit()


def inputzao():
    global opcao
    global hasNewEsp
    global alarme
    opcao = input('\ndigite a opcao desejada\n')
    if(opcao=='0'):
        close_threads(signal.SIGINT,'')
    elif(opcao=='1'):
        if hasNewEsp:
            registerEspSemaphore.set()
            mainMenuSemaphore.clear()
        else:
            print("\nSem esp para cadastrar\n")
            time.sleep(1)
            mainMenuSemaphore.set()
    elif(opcao=='2'):
        espMenuSemaphore.set()
    elif(opcao=='3'):
        alarme=int(not alarme)
        if alarme:
            print("Alarme ativado")
            escreveCSV("Alarme ativado")
        else:
            print("Alarme desativado")
            escreveCSV("Alarme desativado")
        time.sleep(1)
        espMenuSemaphore.set()
    elif(opcao=='4'):
        espMenuSemaphore.clear()
        ligarLed()
    elif(opcao=='5'):
        espMenuSemaphore.clear()
        resetarEsp()
    elif(opcao=='6'):
        espMenuSemaphore.clear()
        mainMenuSemaphore.set()
    else:
        print("opcao inválida, tente novamente")
        inputzao()
        

#trata CTRL+Z
def signal_handler(sig, frame):
    mainMenuSemaphore.clear()
    if(espMenuSemaphore.is_set):
        espMenuSemaphore.clear()
    inputzao()


def menu():
    global hasNewEsp
    global opcao
    global svRunning
    global alarme
    while(svRunning):
        mainMenuSemaphore.wait()
        os.system('cls' if os.name == 'nt' else 'clear')
        if hasNewEsp:
            print(f'''----------------- MENU ----------------- 
# Nova esp para ser cadastrada, digite 1 para adicionar
1- add esp
2- info esp
0- Sair''')
            print("\nPressione CTRL+Z para ativar o input")

        else:
            print(f'''----------------- MENU -----------------
1- add esp
2- info esp
0- Sair''')
            print("\nPressione CTRL+Z para ativar o input")
        time.sleep(3)


def verificaAlarme():
    global contador_disp
    global cliente
    global svRunning
    global alarme
    mixer.init()
    mixer.music.load('beep.mp3')

    while(svRunning):
        tocaAlarme=0
        esp=-1
        if alarme:
            for i in range(contador_disp):
                if cliente[i].statusIn:
                    esp = i
                    tocaAlarme = 1
        if tocaAlarme:
            escreveCSV(f"Alarme foi ativado pela esp ID: {cliente[esp].id}")
            mixer.music.play()

        time.sleep(1)


def escreveCSV(texto):
    global arquivo
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    arquivo.write(f'{dt_string}, {texto}\n')

def inicializaArquivoCSV():
    global arquivo
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
    arquivo = open(dt_string+'.csv', 'w')
    arquivo.write("Horario, Acontecimento\n")


#inicializa semaforos
def semaphoreKeeper():
    registerEspSemaphore.clear()
    espMenuSemaphore.clear()
    mainMenuSemaphore.set()


signal.signal(signal.SIGTSTP, signal_handler)
signal.signal(signal.SIGINT, close_threads)
inicializaArquivoCSV()
t0 = threading.Thread(target=semaphoreKeeper)
t0.daemon = True
t0.start()
t1 = threading.Thread(target=menu)
t1.daemon = True
t1.start()
t2 = threading.Thread(target=verificaAlarme)
t2.daemon = True
t2.start()
t3 = threading.Thread(target=menuEsps)
t3.daemon = True
t3.start()

while svRunning:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()
