# BMS_CLP-CAN---TC-IP-S7-1500-
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

# Referências
- Mais sobre esses drivers e parametros na documentação do python-can(recomendo tentativa de uso do peak-can pois temos esse no laboratório e os drivers são oficiais diferentemente da gambiarra que é necessária para usar o CANdapter): https://python-can.readthedocs.io/en/stable/interfaces.html
- Segue a documentação dos métodos da biblioteca python-can: https://python-can.readthedocs.io/en/stable/message.html

## Biblioteca Socket

Comunicando com o CLP via blocos TCON + TRECV + TSEND (Eu consegui estabelecer comunicação com esse metodo, porém ele preenchia uma DB de forma descontrolada… por isso parti para o snap7 - Caso eu vá utilizar isso algum dia lembre de por algo na variavel “LEN” e também de chamar a função na main)

https://youtu.be/rzl2ULtNQBU
https://www.youtube.com/watch?v=-JoZZY71Br4&ab_channel=Hegamurl 

## snap7
https://snap7.sourceforge.net/
Compatibilidade e configuraçã do TIA portal: https://snap7.sourceforge.net/snap7_client.html#1200_1500
https://python-snap7.readthedocs.io/en/latest/_modules/snap7/util.html
Explicação Areastable e Wordlen:  https://snap7.sourceforge.net/sharp7.html

MODO 1: 

#video 1
https://www.youtube.com/watch?v=Ak6dZx2RnOk

#video 2
https://www.youtube.com/watch?v=2I6d6sRIl6Q&t=181s

git
https://github.com/bsarante/canalyoutube/tree/main

MODO 2:
Vídeos do Car#
https://www.youtube.com/watch?v=xSTfmCdepyw
https://www.youtube.com/watch?v=Eo8NyNE1bRY

git
https://github.com/Mareh07/plcwars-python-snap7


3º visão
https://www.youtube.com/watch?v=BKnK4AT_WKs&t=222s

4º Visão
Foi o que mais deu certo
https://www.youtube.com/watch?v=nN_475fmcKY



