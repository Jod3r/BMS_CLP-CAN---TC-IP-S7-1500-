import struct #Para desempacotar o byteArray

from bms_checksum import checksum

def enderecamento1(id, value):
    idsx = [1712, 1713, 1714, 1715, 1716]
    me = [500, 504, 508, 512, 516, 520, 524, 528, 532, 536, 540, 544, 548, 552, 556, 560, 564, 568, 572, 576]
    
    if id not in idsx:
        return None
    
    data_list = list(value)  # Convertendo o bytearray para lista
    soma =  sum(data_list) - data_list[7]
    data3 = checksum(id,soma,data_list[7])
    if data3 == False: # Seguindo a recomendação do fabricante de descartar os dados com falha de checkSum
        return None
    
    index = idsx.index(id)
    me = me[index*4 : index*4 + 4]
    if index == 0:
        data0 = struct.unpack('<h', value[0:2])[0] / 10.0 #aqui estou desempacotando o bytearray em tupla e já pegando a posição 0 da tupla -> int
        data1 = struct.unpack('<h', value[2:4])[0] / 10.0 #big-Endian h - signed and H unsigned for 2 bytes and b/B for 1 byte
        data2 = struct.unpack('<H', value[4:6])[0] / 10.0
    if index == 2:
        data0 = struct.unpack('<H', value[0:2])[0] / 10.0 
        data1 = struct.unpack('<H', value[2:4])[0] / 10.0 
        data2 = struct.unpack('<H', value[4:6])[0] / 10.0
    elif index == 3 or index == 4:
        data0 = struct.unpack('<H', value[0:2])[0] / 10.0
        data1 = struct.unpack('<H', value[2:4])[0] / 10.0
        data2 = struct.unpack('<H', value[4:6])[0]
    elif index == 1:
        data0 = struct.unpack('<H', value[0:2])[0]
        data1 = struct.unpack('<H', value[2:4])[0]
        data2 = struct.unpack('<H', value[4:6])[0]

    return (*me, data0, data1, data2, data3)

def enderecamento2(id, value):
    if id != 1717:
        return None
    
    data_list = list(value)  # Convertendo o bytearray para lista
    soma =  sum(data_list) - data_list[7]
    data_list[7] = checksum(id,soma,data_list[7])
    if data_list[7] == False: # Seguindo a recomendação do fabricante de descartar os dados com falha de checkSum
        return None
    data_list[5] = data_list[5] * 0.5
    data_list[6] = data_list[6] * 0.5
    me = [580, 584, 588, 592, 596, 600, 604, 608]
    if id == 1717:
        return tuple(me + data_list)

def enderecamento3(id, value): #6b6
    me = [638, 642, 646, 650, 654, 658, 662, 666]
    valor = value
    data = []

    if id == 1718:
        me_range = me[0:4]
        data.append(struct.unpack('<H', valor[0:2])[0])
        data[1:3] = [struct.unpack('<H', valor[i : i + 2])[0] / 100.0 for i in range(2, 8, 2)] #range i começa em 2 com step de 2 até 8 [2:4],[4:6] e [6:8]
    elif id == 1719:
        me_range = me[4:8]
        data.append(struct.unpack('<H', valor[0:2])[0])
        data[1:3] = [struct.unpack('<H', valor[i : i + 2])[0] / 10.0 for i in range(2, 8, 2)] #dividindo por 10 e acima por 100
    else:
        return None

    return tuple(me_range + data)

def operacaobitabit(data0):
    bit = [1 << i for i in range(15, -1, -1)]
    bit.reverse()
    return tuple(bool(data0 & b) for b in bit)

def enderecamento4(id, value):
    idsx = [1720, 1721]

    if id not in idsx:
        return None
    
    me = [612, 613, 614, 615, 616, 617, 621, 625, 626, 627, 628, 629, 630, 634]
    me_range = [0, 7] if id == idsx[0] else [7, 14]
    data_list = list(value)  # Convertendo o bytearray para lista
    soma =  sum(data_list) - data_list[7]
    data3 = checksum(id,soma,data_list[7])
    if data3 == False: # Seguindo a recomendação do fabricante de descartar os dados com falha de checkSum
        return None
    data0 = int.from_bytes(data_list[0:2], 'little')
    data1 = int.from_bytes(data_list[2:4], 'little')
    data2 = int.from_bytes(data_list[4:6], 'little')
    
    result = me[me_range[0]:me_range[1]]
    result += operacaobitabit(data0)
    result += operacaobitabit(data1)
    result += operacaobitabit(data2)

    return tuple(result) + (data3,) + (id,) +(value,) #esse aqui fiz um pouco diferente, para ler no SQL vou usaro bytearray mesmo e indexar ao id
