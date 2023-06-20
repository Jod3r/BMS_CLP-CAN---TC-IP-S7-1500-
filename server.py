import socket

HOST = '127.0.0.1'  # Endereço IP do servidor
PORT = 1234  # Porta para a conexão

# Cria o socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))  # Associa o socket ao endereço IP e à porta
s.listen(1)  # Aguarda por conexões de um cliente

print(f'Aguardando por conexões em {HOST}:{PORT}...')

while True:
    conn, addr = s.accept()  # Aceita a conexão do cliente
    print(f'Conexão estabelecida com {addr[0]}:{addr[1]}')

    data = conn.recv(1024)  # Recebe os dados do cliente (tamanho máximo do buffer é 1024 bytes)
    if data:
        msg = data.decode()  # Decodifica a mensagem recebida de bytes para string
        print(f'Mensagem recebida: {msg}')
    else:
        print('Conexão fechada pelo cliente.')
    conn.close()  # Fecha a conexão com o cliente
    
