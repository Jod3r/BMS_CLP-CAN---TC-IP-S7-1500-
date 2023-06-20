#Instruções gerais:

#get/put deve estar ativado no CLP
#O DB deve estar com o optimized desabilitado

# observando quando envio algo por exemplo MD500 ele envia para a 500, mas acredito que envie lixo para 499, 501,502,503. Também se houver outra memoria 500, não importa se o tipo seja diferente(MW e MD, não importa), é melhor utilizar outra faixa de memorias
#Suponho que isso ocorra por conta do seguinte:

#SInt 8 bits MB00 -128 a +127
#Int 16 bits MW02 -32768 a +32767
#UInt 16 bits MW04 0 a +65535
#Word 16 bits MW06 0 a +65535
#Real 32 bits MD08 1.175495 ** -38 a 3.402823 ** +38
#Real//Float//Dword/MD
#uma curiosidade é que esse software limitou em + ou -1.6214205944524335 ** 20 

import can
import snap7.client as c #utilizado para estabelecer comunicação ethernet
from snap7.util import *
from snap7.types import *
import time
from datetime import datetime
import subprocess #Utilizado para escrever comandos no terminal shell
import sqlite3

from bms_Enderecamento import enderecamento1,enderecamento2,enderecamento3,enderecamento4 #observe que os enderecamentos foram feitos especificamente para o perfil montado por mim. Existem ajustes em tudo.
from bms_ES_PLC import ReadMemory,WriteMemory

ids = [1712, 1713, 1714, 1715, 1716, 1717, 1718, 1719, 1720, 1721]   #lista de todos os ID's que tem informação no BMS
channel = 'can0' #interface simulada 'vcan0' interface real do lab 'can0'

#   Configuração do bus CAN
buffer_siz = 15 # Define um tamanho de buffer menor (por exemplo, 15 mensagens)
b1 = can.Bus(channel, interface = 'socketcan') # seta as configurações do barramento CAN
escuta = can.BufferedReader(b1,buffer_siz) # inicia uma fila de mensagens
notifica = can.Notifier(b1, [escuta]) # notifica uma nova mensagem
timeout = 1 #tempo em segundos para acusar falha CAN uso na função monitorar

# Configuração do socket TCP
HOST = '192.168.180.10'  # Endereço IP do client (CLP) // no protocolo Ethernet quem inicia a comunicação par a par é chamado de cliente
PORT = 102  # Porta para a conexão 2000 ou sem
RACK = 0    # Rack do PLC (Consegue ver em device view - vai ter só 0)
SLOT = 1    # Slot do PLC (Dentro do rack vai ter o PS, CPU, DI e DQ, a CPU está em 1)

plc = c.Client()
plc.connect(HOST,RACK,SLOT) # IP adress, rack, slot, port (Nesse caso não precisou) (from Hardware settings)
print(plc.get_cpu_state())
print(plc.get_connected())
time.sleep(1) #Tempo para poder checar a conexão

# Configuração da base de dados SQLite
conn = sqlite3.connect('BMS_CLP.db')  # Conecta ou cria um novo arquivo de banco de dados
c = conn.cursor()  # Cria um cursor para realizar operações no banco de dados

# Cria a tabela para armazenar as mensagens com colunas separadas
c.execute('''CREATE TABLE IF NOT EXISTS mensagens
             (data_hora TEXT, Memoria_1 INTEGER, dado_lido_1 REAL, Memoria_2 INTEGER, dado_lido_2 REAL, Memoria_3 INTEGER, dado_lido_3 REAL, Memoria_4 INTEGER, dado_lido_4 REAL, Memoria_5 INTEGER, dado_lido_5 REAL, Memoria_6 INTEGER, dado_lido_6 REAL, Memoria_7 INTEGER, dado_lido_7 REAL, Memoria_8 INTEGER, dado_lido_8 REAL, id INTEGER, bytearray BLOB)''')
# TEXT - TEXTO | INTEGER - INTEIRO | REAL - REAL | BLOB (Binary Large object - bytearray)
conn.commit()  # Confirma a criação da tabela'''

def send_DB(dado1,dado2,dado3,dado4,dado5,dado6,dado7,dado8,dado9,dado10,dado11,dado12,dado13,dado14,dado15,dado16,dado17,dado18):
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    # Insere os valores da tupla nas colunas correspondentes no banco de dados
    c.execute("INSERT INTO mensagens (data_hora, Memoria_1, dado_lido_1, Memoria_2, dado_lido_2, Memoria_3, dado_lido_3, Memoria_4, dado_lido_4, Memoria_5, dado_lido_5, Memoria_6, dado_lido_6, Memoria_7, dado_lido_7, Memoria_8, dado_lido_8, id, bytearray) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (date_time,dado1,dado2,dado3,dado4,dado5,dado6,dado7,dado8,dado9,dado10,dado11,dado12,dado13,dado14,dado15,dado16,dado17,dado18))
    conn.commit()  # Confirma a inserção dos dados

def monitorar(tempo_max):
    buffer = [None,None,None,None,None,None,None,None,None,None]  # tuple para armazenar as mensagens dos IDs específicos
    tempo_inicial = time.time()  # Tempo inicial em segundos

    # Tenta obter todas as mensagens dos IDs específicos
    while any(elem is None for elem in buffer) and time.time() - tempo_inicial < tempo_max:  # Continua até que todas as posições sejam preenchidas OU esgotar o tempo
        m = escuta.get_message(timeout=0.008)  # Obtém a próxima mensagem da fila com timeout curto 8 ms
        if m is not None and m.arbitration_id in ids:
            posicao = ids.index(m.arbitration_id)  # Obtém a posição com base no ID
            buffer[posicao] = m.data
    if any(elem is None for elem in buffer):
        # Algum elemento do buffer está faltando, indicando uma falha
        print("Falha na comunicação CAN. Algumas mensagens não foram recebidas.")
        WriteMemory(plc,670,0,S7WLBit,True)
    else:
        WriteMemory(plc,670,0,S7WLBit,False)
    # Limpar o buffer de recepção
    while escuta.get_message(timeout=0.0001): #reiniciando o buffer, uma gambiarra para limpar. Lendo o barramento e descartando. Tentar achar algo mais eficiente.
        pass
    return tuple(buffer) #Apos ler todos os ids eu faço uma limpeza do buffer para manter os dados mais atualizados, como o BMS irá enviar as mensagens em um tempo bem curto 8 ou 16 ms não acredito que vamos ter problemas com perca de dados
    #Essa limpeza no buffer é importante, pois quando eu retiro o cabo do PEAK, e mantenho o USB conectado o software fica lendo esse buffer, com o BMS desconectado, Então dessa forma leio o dado mais atualizado e se o cabo se romper acusa falha CAN.
# Loop principal infinito.
while True:
    #Teste de tempo do loop

    #now = datetime.now()
    #date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    #print(date_time)

    # Lógica para verificar conexão do PC_BMS no PLC "is blinking is ok"
    x = ReadMemory(plc,670,1,S7WLBit)
    x = not x
    WriteMemory(plc,670,1,S7WLBit,x)

    mensagem_can = monitorar(timeout) #Pode chegar um tuple [None,None,None,None,None,None,None,None,None,None]

    if mensagem_can != [None,None,None,None,None,None,None,None,None,None]:
        mensagem0 = mensagem_can[0] #data id 1712
        mensagem1 = mensagem_can[1]
        mensagem2 = mensagem_can[2]
        mensagem3 = mensagem_can[3]
        mensagem4 = mensagem_can[4] #data id 1716
        mensagem5 = mensagem_can[5]
        mensagem6 = mensagem_can[6]
        mensagem7 = mensagem_can[7]
        mensagem8 = mensagem_can[8]
        mensagem9 = mensagem_can[9] #data id 1721
        mensagem_can = [None,None,None,None,None,None,None,None,None,None]
        #Ids 1712 - 1716 com o enderecamento 1
        mensagem_enderecada1_0 = enderecamento1(ids[0],mensagem0)
        mensagem_enderecada1_1 = enderecamento1(ids[1],mensagem1)
        mensagem_enderecada1_2 = enderecamento1(ids[2],mensagem2)
        mensagem_enderecada1_3 = enderecamento1(ids[3],mensagem3)
        mensagem_enderecada1_4 = enderecamento1(ids[4],mensagem4)
        mensagens_1 = [mensagem_enderecada1_0, mensagem_enderecada1_1, mensagem_enderecada1_2, mensagem_enderecada1_3, mensagem_enderecada1_4]
        #Ids 1717 com o enderecamento 2
        mensagem_enderecada2 = enderecamento2(ids[5],mensagem5)
        #Ids 1718 - 1719 com o enderecamento 3
        mensagem_enderecada3_0 = enderecamento3(ids[6],mensagem6)
        mensagem_enderecada3_1 = enderecamento3(ids[7],mensagem7)
        mensagens_3 = [mensagem_enderecada3_0, mensagem_enderecada3_1]
        #Ids 1720 - 1721 com o enderecamento 4
        mensagem_enderecada4_0 = enderecamento4(ids[8],mensagem8)
        mensagem_enderecada4_1 = enderecamento4(ids[9],mensagem9)
        mensagens_4 = [mensagem_enderecada4_0, mensagem_enderecada4_1]
        
        for mensagem_enderecada1 in mensagens_1: #estou iterando a variavel dos enderecamentos 1 no if abaixo
            if mensagem_enderecada1 is not None:
                MD1, MD2, MD3, MD4, M_SD1, M_SD2, M_SD3, M_SD4 = mensagem_enderecada1

                WriteMemory(plc,MD1,0,S7WLReal,M_SD1)
                WriteMemory(plc,MD2,0,S7WLReal,M_SD2)
                WriteMemory(plc,MD3,0,S7WLReal,M_SD3)
                WriteMemory(plc,MD4,0,S7WLReal,M_SD4)

                send_DB(MD1,M_SD1,MD2,M_SD2,MD3,M_SD3,MD4,M_SD4,None,None,None,None,None,None,None,None,None,None)

        if mensagem_enderecada2 is not None: #como só tem um id nesse enderecamento, não precisa iterar
            MD1, MD2, MD3, MD4, MD5, MD6, MD7, MD8, M_SD1, M_SD2, M_SD3, M_SD4, M_SD5, M_SD6, M_SD7, M_SD8 = mensagem_enderecada2
            WriteMemory(plc,MD1,0,S7WLReal,M_SD1)
            WriteMemory(plc,MD2,0,S7WLReal,M_SD2)
            WriteMemory(plc,MD3,0,S7WLReal,M_SD3)
            WriteMemory(plc,MD4,0,S7WLReal,M_SD4)
            WriteMemory(plc,MD5,0,S7WLReal,M_SD5)
            WriteMemory(plc,MD6,0,S7WLReal,M_SD6)
            WriteMemory(plc,MD7,0,S7WLReal,M_SD7)
            WriteMemory(plc,MD8,0,S7WLReal,M_SD8)

            send_DB(MD1,M_SD1,MD2,M_SD2,MD3,M_SD3,MD4,M_SD4,MD5,M_SD5,MD6,M_SD6,MD7,M_SD7,MD8,M_SD8,None,None)

        for mensagem_enderecada3 in mensagens_3: #estou iterando a variavel dos enderecamentos 3 no if abaixo
            if mensagem_enderecada3 is not None:
                MD1, MD2, MD3, MD4, M_SD1, M_SD2, M_SD3, M_SD4 = mensagem_enderecada3
                WriteMemory(plc,MD1,0,S7WLReal,M_SD1)
                WriteMemory(plc,MD2,0,S7WLReal,M_SD2)
                WriteMemory(plc,MD3,0,S7WLReal,M_SD3)
                WriteMemory(plc,MD4,0,S7WLReal,M_SD4)

                send_DB(MD1,M_SD1,MD2,M_SD2,MD3,M_SD3,MD4,M_SD4,None,None,None,None,None,None,None,None,None,None)

        for mensagem_enderecada4 in mensagens_4: #estou iterando a variavel dos enderecamentos 4 no if abaixo
            if mensagem_enderecada4 is not None:
            #plc/byte/bit/tipo/mensagem
                send_DB(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,mensagem_enderecada4[56],mensagem_enderecada4[57]) #Estou enviado para o DB o id e o value completo, sem o checksum

                WriteMemory(plc,mensagem_enderecada4[0],0,S7WLBit,mensagem_enderecada4[7])
                WriteMemory(plc,mensagem_enderecada4[0],1,S7WLBit,mensagem_enderecada4[8])
                WriteMemory(plc,mensagem_enderecada4[0],2,S7WLBit,mensagem_enderecada4[9])
                WriteMemory(plc,mensagem_enderecada4[0],3,S7WLBit,mensagem_enderecada4[10])
                WriteMemory(plc,mensagem_enderecada4[0],4,S7WLBit,mensagem_enderecada4[11])
                WriteMemory(plc,mensagem_enderecada4[0],5,S7WLBit,mensagem_enderecada4[12])
                WriteMemory(plc,mensagem_enderecada4[0],6,S7WLBit,mensagem_enderecada4[13])
                WriteMemory(plc,mensagem_enderecada4[0],7,S7WLBit,mensagem_enderecada4[14])
                WriteMemory(plc,mensagem_enderecada4[1],0,S7WLBit,mensagem_enderecada4[15])
                WriteMemory(plc,mensagem_enderecada4[1],1,S7WLBit,mensagem_enderecada4[16])
                WriteMemory(plc,mensagem_enderecada4[1],2,S7WLBit,mensagem_enderecada4[17])
                WriteMemory(plc,mensagem_enderecada4[1],3,S7WLBit,mensagem_enderecada4[18])
                WriteMemory(plc,mensagem_enderecada4[1],4,S7WLBit,mensagem_enderecada4[19])
                WriteMemory(plc,mensagem_enderecada4[1],5,S7WLBit,mensagem_enderecada4[20])
                WriteMemory(plc,mensagem_enderecada4[1],6,S7WLBit,mensagem_enderecada4[21])
                WriteMemory(plc,mensagem_enderecada4[1],7,S7WLBit,mensagem_enderecada4[22])

                WriteMemory(plc,mensagem_enderecada4[2],0,S7WLBit,mensagem_enderecada4[23])
                WriteMemory(plc,mensagem_enderecada4[2],1,S7WLBit,mensagem_enderecada4[24])
                WriteMemory(plc,mensagem_enderecada4[2],2,S7WLBit,mensagem_enderecada4[25])
                WriteMemory(plc,mensagem_enderecada4[2],3,S7WLBit,mensagem_enderecada4[26])
                WriteMemory(plc,mensagem_enderecada4[2],4,S7WLBit,mensagem_enderecada4[27])
                WriteMemory(plc,mensagem_enderecada4[2],5,S7WLBit,mensagem_enderecada4[28])
                WriteMemory(plc,mensagem_enderecada4[2],6,S7WLBit,mensagem_enderecada4[29])
                WriteMemory(plc,mensagem_enderecada4[2],7,S7WLBit,mensagem_enderecada4[30])
                WriteMemory(plc,mensagem_enderecada4[3],0,S7WLBit,mensagem_enderecada4[31])
                WriteMemory(plc,mensagem_enderecada4[3],1,S7WLBit,mensagem_enderecada4[32])
                WriteMemory(plc,mensagem_enderecada4[3],2,S7WLBit,mensagem_enderecada4[33])
                WriteMemory(plc,mensagem_enderecada4[3],3,S7WLBit,mensagem_enderecada4[34])
                WriteMemory(plc,mensagem_enderecada4[3],4,S7WLBit,mensagem_enderecada4[35])
                WriteMemory(plc,mensagem_enderecada4[3],5,S7WLBit,mensagem_enderecada4[36])
                WriteMemory(plc,mensagem_enderecada4[3],6,S7WLBit,mensagem_enderecada4[37])
                WriteMemory(plc,mensagem_enderecada4[3],7,S7WLBit,mensagem_enderecada4[38])

                WriteMemory(plc,mensagem_enderecada4[4],0,S7WLBit,mensagem_enderecada4[39])
                WriteMemory(plc,mensagem_enderecada4[4],1,S7WLBit,mensagem_enderecada4[40])
                WriteMemory(plc,mensagem_enderecada4[4],2,S7WLBit,mensagem_enderecada4[41])
                WriteMemory(plc,mensagem_enderecada4[4],3,S7WLBit,mensagem_enderecada4[42])
                WriteMemory(plc,mensagem_enderecada4[4],4,S7WLBit,mensagem_enderecada4[43])
                WriteMemory(plc,mensagem_enderecada4[4],5,S7WLBit,mensagem_enderecada4[44])
                WriteMemory(plc,mensagem_enderecada4[4],6,S7WLBit,mensagem_enderecada4[45])
                WriteMemory(plc,mensagem_enderecada4[4],7,S7WLBit,mensagem_enderecada4[46])
                WriteMemory(plc,mensagem_enderecada4[5],0,S7WLBit,mensagem_enderecada4[47])
                WriteMemory(plc,mensagem_enderecada4[5],1,S7WLBit,mensagem_enderecada4[48])
                WriteMemory(plc,mensagem_enderecada4[5],2,S7WLBit,mensagem_enderecada4[49])
                WriteMemory(plc,mensagem_enderecada4[5],3,S7WLBit,mensagem_enderecada4[50])
                WriteMemory(plc,mensagem_enderecada4[5],4,S7WLBit,mensagem_enderecada4[51])
                WriteMemory(plc,mensagem_enderecada4[5],5,S7WLBit,mensagem_enderecada4[52])
                WriteMemory(plc,mensagem_enderecada4[5],6,S7WLBit,mensagem_enderecada4[53])
                WriteMemory(plc,mensagem_enderecada4[5],7,S7WLBit,mensagem_enderecada4[54])

                WriteMemory(plc,mensagem_enderecada4[6],0,S7WLReal,mensagem_enderecada4[55])
        
        #print("fim") #só para testar a velocidade de leitura
        #now = datetime.now()
        #date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        #print(date_time)

        #time.sleep(1) #Durante a operação é melhor tirar [Cara nunca ative esse código já está lento...acredito que por conta do database, fiz alguns ajustes para otimizar, vou testar ainda]
