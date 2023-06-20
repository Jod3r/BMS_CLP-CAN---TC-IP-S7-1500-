#!/bin/bash

chmod +x dependencias_real.sh
./dependencias_real.sh
python3 bms_clp.py &

# Salvar o ID do processo do script Python em uma variável
pid=$!

# Função para matar o processo do script Python
matar_script_python() {
  echo -e "\nMatando o script Python..."
  kill $pid
  exit 0
}

# Função para trazer o processo do script Python para o primeiro plano
trazer_para_primeiro_plano() {
  echo -e "\nTrazendo o script Python para o primeiro plano..."
  fg %1
}

# Aguardar entrada do usuário para matar o script Python, trazer para o primeiro plano ou verificar se o processo morreu
while true; do
  read -n 1 -p "O processo ainda está rodando. Pressione 'q' para matar ou 'f' para trazer para o primeiro plano : " input
  if [[ $input == "q" ]]; then
    matar_script_python
  elif [[ $input == "f" ]]; then
    trazer_para_primeiro_plano
  fi

  # Verificar se o processo do script Python ainda está em execução
  kill -0 $pid > /dev/null 2>&1
  if [[ $? != 0 ]]; then
    echo -e "\nO processo do script Python morreu. Verifique se ocorreu algum erro."
    exit 1
  fi
done

