#!/bin/bash

echo "instalando dependencias do linux(ubuntu)" #precisa ser feito apenas uma vez na maquina
sudo apt install can-utils -y
sudo apt install net-tools
echo "dependencias python" 
sudo pip install python-can 

echo "ligando interface CAN FISICA" #deve ser feito sempre na inicialização
sudo ip link set can0 type can bitrate 500000 
sudo ip link set up can0
echo "Checagem se a rede realmente está ligada"
ifconfig can0
