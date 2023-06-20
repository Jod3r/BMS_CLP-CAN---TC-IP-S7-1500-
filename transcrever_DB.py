import sqlite3
import csv

DB = 'BMS_CLP.db'
CSV = 'mensagens1.csv'
#cabecalho = ['timestamp', 'data_hex', 'arbitration_id']
cabecalho = ['data_hora', 'Memoria_1', 'dado_lido_1', 'Memoria_2', 'dado_lido_2', 'Memoria_3', 'dado_lido_3', 'Memoria_4', 'dado_lido_4', 'Memoria_5', 'dado_lido_5', 'Memoria_6', 'dado_lido_6', 'Memoria_7', 'dado_lido_7', 'Memoria_8', 'dado_lido_8', 'id', 'bytearray']

# Conecta-se à base de dados SQLite
conn = sqlite3.connect(DB) 
c = conn.cursor()

# Lê os dados da tabela de mensagens
c.execute("SELECT * FROM mensagens")
dados = c.fetchall()

# Escreve os dados em um arquivo CSV
with open(CSV, 'w', newline='') as arquivo_csv:
    escritor_csv = csv.writer(arquivo_csv)
    # Escreve o cabeçalho do CSV
    escritor_csv.writerow(cabecalho)
    # Escreve os dados das mensagens
    escritor_csv.writerows(dados)

print("Dados transcritos para o arquivo CSV: ", CSV)
