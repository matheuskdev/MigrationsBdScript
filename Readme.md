Esse script consiste em migração de dados entre dois bancos diferentes.
As tabelas que estão sendo utlizadas são do glpi versão 9.5.7.
Aconselho realizar todos os processos com uma venv python.

Versão do Python utilizada no script: 
    3.11.0
    S.O : Win10
    
*Com a pasta do projeto aberta digite no terminal:
    python -m venv env

*Para ativar a venv digite no terminal:
    ./env/Scripts/Activate.ps1

*Caso o seu windows não aceite, abra o PowerShell como administrador e digite:
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    
    Concorde com:
    S ou Y

*Para o funcionamento correto do script, deve ser instalado as seguintes bibliotecas:

    pip install mysql-connector
    pip install cx_Oracle
    pip install pandas
    pip install logging

