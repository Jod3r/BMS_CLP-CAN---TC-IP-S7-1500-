def checksum(id_lido,value,checksum):
    check = id_lido << 8
    check = check + value
    check = int(check) & 0xFF
    if check == checksum: #Obs value deve vir a soma de byte a byte, cuidado ao somar bytes par a par não é o jeito correto. Mesmo assim pode dar certo pois o byte pode vir x00x7A
        return True
    else:
        print("Falha na comunicação CAN. CHECKSUM.")
        return False
