Esse trabalho é uma continuação do trabalho do Paul, que também se encontra no seguinte endereço no github:
https://github.com/paulatufpr/icmicrorredes

Git dedicado ao desenvolvimento do metodo de leitura para os equipamentos que comunicam via CAN no laboratorio de microrredes.
O desenvolvimento sera dividido em duas frentes: python para ser usado enquanto a solucao no MOXA nao esta pronta e C caso seja possivel usar o moxa para controle dos BMS.

# À utilização dos scripts feitos:

## Dependencias
- Alguns scripts bash foram criados caso seja do interesse o uso dos scripts em ambiente linux, a inicialização não precisa ser feita manualmente apenas rodar o script desejado(com hardware real ou simulado), checar dependencias_real.sh e dependencias_sim.sh
```bash
Python 3.10.6 (main, Nov 14 2022, 16:10:14) [GCC 11.3.0] on linux
pip install python-can
pip install sqlite3 # não precisei rodar no linux porém talvez seja um problema no windows.
sudo apt install can-utils # para interface tanto virtual como geração de dados e sniffing

#Inicialização do CAN no linux

$ modprobe can0 # vcan0 se for rede virtual
$ sudo ip link add dev can0 type can bitrate 500000 # vcan0 se for rede virtual e não precisa do bitrate
$ sudo ip link set up can0 # vcan0 se for rede virtual
$ cangen vcan0 # caso precise gerar trafego aleatório em interface virtual(depende do pacote can-utils)
```


## bms_microrredes
- Se utilizado em ambiente linux pode ser rodado completamente pelo script run.sh.
- Agora arquivo principal compreendendo os 3 que eram separados, ficou melhor rodar apenas um processo e mais facil de mata-lo caso preciso.

-  Está bem comentado, apenas o que falta para implementação é o ajuste ao inves de usar o socketCAN o programa será rodado em uma maquina windows o que envolve mudar os parametros na variavel 
```python
b1 = can.Bus(channel='vcan0', interface='socketcan')
```
- Além da instalação de drivers compatíveis com os leitores CAN do laborátório.

- Mais sobre esses drivers e parametros na documentação do python-can(recomendo tentativa de uso do peak-can pois temos esse no laboratório e os drivers são oficiais diferentemente da gambiarra que é necessária para usar o CANdapter): https://python-can.readthedocs.io/en/stable/interfaces.html
  
- Agora o socet TCP lida com o fato do servidor externo não estar ligado e trava o processo até que a conexão seja realizada novamente;

```bash 
Erro de conexão: [Errno 111] Connection refused
Tentando novamente em 1 segundo...
```

- O tempo de sleep deve ser ajustado de acordo com a necessidade do CLP 
```python
while True:
    mensagem = monitorar()
    if mensagem is not None:
        msg_tuple = (mensagem.timestamp, mensagem.data.hex(), mensagem.arbitration_id) 
        print(msg_tuple)
        salvar_tupla_no_banco_de_dados(msg_tuple)  
        enviar_tupla_via_tcp(msg_tuple)  
-->#time.sleep(1)   # tempo arbitário 
```

- Deve ser feita a configuração dos métodos que seram utilizados na variável mensagem.
```python
msg_tuple = (mensagem.timestamp, mensagem.data.hex(), mensagem.arbitration_id)
```

- Segue a documentação dos métodos da biblioteca python-can: https://python-can.readthedocs.io/en/stable/message.html
  
 
## db_BMS
- Foi implementado por meio da função salvar_tupla_no_banco_de_dados no bms_microrredes.

- Roda uma instancia de uma base de dados extremamente leve que não precisa de configuração nem instalação de programas. O tempo de amostra pode ser ajustado novamente pelo sleep no loop principal. O codigo foi feito sem muito pensamento até pela falta de tempo então se possível no futuro fazer algo mais robusto.
  

## transcrever_DB
- É um script apenas para a leitura dos dados em formato CSV(facilidade de leitura no excel) para uso de quem necessitar dos dados.

## server
- Pode ser usado na maquina local para debugar qualquer tipo de problema com o leitor_BMS ou a comunicação mesmo.
  
  
  


## Comentários adicionais: 
- Nunca nomear qualquer codigo que envolve a biblioteca python-can com as letras "can" escritas dessa exata forma ou o codigo não rodará;
- Os endereços ip e portas devem ser alterados para os endereços adequados do laboratório;
- Lembrar que o código foi desenvolvido em ambiente linux e portanto poderão ocorrer problemas caso apenas rodem os scripts em uma maquina windows.
- nesse projeto aprendi três métodos para extrair um bytearray posso usar os seguintes métodos:
struct.unpack('<H', valor[i : i + 2]
int.from_bytes(value[4:6], byteorder='little')
data_list = list(value)  # Convertendo o bytearray para lista

-função verifica_falhaCAN: Precisa ser estudada...
-Documentar certinho

-Vou criar um scrip run.sh que ira rodar o dependencias_real.sh e o bms_clp (que ira fazer todo o processo)
Para executar o script abra o terminal e navegue utilizando os comandos "cd" até a pasta do "run.sh" e execute os seguintes comandos:

chmod +x run.sh
./run.sh

Pronto o software estará rodando. Cuidado que se houver algum tipo de falha de comunicação ou queda de energia, ele não reestabelece sozinho. (Talvez seja o caso de implementar algo nesse sentido)

A idéia é que o programa deixe facil a questão de segundo plano, primeiro plano e matar o processo. Mas caso feche o terminal sem matar o processo...
use o comado "ps aux" - vai listar os processos e veja os PID quando encontrar execute "kill PID" (Valor encontrado)
uma forma de encontrar o PID é usar o pgrep python (Ele vai listar os PIDs que tem python, você pode subir na lista e verificar se o nome bate com o script. hoje o nome é bms_clp.py possivel seja encontrado por esse nome)





