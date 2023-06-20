#tentei seguir nessa linha, mas não conseguir finalizar

senha = "microredes" #sua senha root para reestabelecer comunicação CAN

def verificar_falha_can(interface_can): #ainda não funciona 100%...
    try:
        bus = can.interface.Bus(interface_can, interface = 'socketcan')
        message = bus.recv(timeout=1)
        WriteMemory(plc,670,0,S7WLBit,False)
    except can.CanError:
        print("Falha de comunicação CAN detectada! Tentando reestabelecer...")
        WriteMemory(plc,670,0,S7WLBit,True)
        # Esvazia o buffer sem processar as mensagens restantes
        escuta.flush()
        try:
            # Comando para reestabelecer a interface CAN
            cmd1 = f"sudo ip link set {interface_can} type can bitrate 500000"
            cmd2 = f"sudo ip link set up {interface_can}"

            # Definindo a variável de ambiente SUDO_ASKPASS
            env = {"SUDO_ASKPASS": "echo"}
 
            # Executando o comando com sudo
            processo1 = subprocess.Popen(cmd1, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
            processo2 = subprocess.Popen(cmd2, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
            saida, erro = processo1.communicate(senha + '\n')
            saida, erro = processo2.communicate(senha + '\n')

        except OSError as e:
            if "Network is down" in str(e):
                print("Erro de rede: A rede está indisponível ou inativa.")
            else:
                print("Erro ao executar o comando:", str(e))
    finally:
        bus.shutdown()