#Importando todas as libs a serem utlizadas.
import mysql.connector
import cx_Oracle
import pandas as pd
from datetime import date
import logging
import csv

log_format = 'DtTm: %(asctime)s -- Lvl: %(levelname)s -- Arqv: %(filename)s -- Msg:%(message)s'
logging.basicConfig(filename='chamado_ti.log',
                    # w -> sobrescreve o arquivo a cada log
                    # a -> não sobrescreve o arquivo
                    filemode='a',
                    level=logging.DEBUG,
                    format=log_format)

logger = logging.getLogger('root')

if int(date.today().strftime('%d')) == 1:



    conn_MySQL = mysql.connector.connect(
        host='',
        database='',
        user='',
        password='')
    cursor_MySQL = conn_MySQL.cursor()

    if conn_MySQL.is_connected():
        logger.info('Banco de dados MySQL Conectado')
    else:
        logger.error('Falha ao conectar com o Banco de dados MySQL')



    query = ('''SELECT 
                        tkt.id ID,
                        DATE_FORMAT(STR_TO_DATE(tkt.date, '%Y-%m-%d %H:%i:%s'), 
                                    '%d-%m-%Y %H:%i:%s') as DT_ABERTURA_CHAMADO,
                        tkt.users_id_recipient COD_USUARIO,
                CASE 
                        WHEN tkt.status = 1 THEN 'Novo'
                        WHEN tkt.status = 2 THEN 'Atribuido/Em Atendimento'
                        WHEN tkt.status = 5 THEN 'Solucionado'
                        WHEN tkt.status = 6 THEN 'Fechado'
                        WHEN tkt.is_deleted = 1 THEN 'Chamado Deletado'
                END     STATUS_CHAMADO,

                        DATE_FORMAT(STR_TO_DATE(tkt.date_mod, '%Y-%m-%d %H:%i:%s'),
                                '%d-%m-%Y %H:%i:%s') AS DT_SOLUCAO_FECHAMENTO_CHAMADO,

                        tkt.locations_id COD_SETOR_GLPI,
                        usu.name NOME_USUARIO_GLPI,
                        loc.name NOME_SETOR_GLPI,

                        DATE_FORMAT(STR_TO_DATE(sysdate(), '%Y-%m-%d %H:%i:%s'), 
                                    '%d-%m-%Y %H:%i:%s') as DT_INTEGRACAO

                FROM 
                        glpi_tickets   tkt,
                        glpi_users     usu,
                        glpi_locations loc  

                WHERE   tkt.users_id_recipient = usu.id
                AND     tkt.locations_id = loc.id  
                AND 	tkt.is_deleted != 1
                AND tkt.status IN (5,6)
                AND tkt.date_mod IS NOT NULL  
                ORDER BY tkt.id''')



    df = pd.read_sql(query, conn_MySQL)
    try:
        if ( df.to_csv("importar_ti.csv",
            encoding = 'utf-8',
            index = False, sep= ',') != False ) :
            logger.info('Arquivo gerado com sucesso.')
        else:
            logger.warning('Algo nao saiu como o esperado.')
    except ValueError:
        logger.warning('Erro.')

    conn_MySQL.close()
    cursor_MySQL.close()




    cx_Oracle.init_oracle_client(lib_dir=r"C:\Oracle\instantclient_21_7",
                                config_dir=r"C:\orant\NETWORK\ADMIN\TNSNAMES.ORA")
    user = ""    
    password = ""  
    host = ""   
    port = ""
    database = ""    
    conn_Oracle = cx_Oracle.connect(user+"/"+password+"@"+host+":"+port+"/"+database) 
    cursor_Oracle = conn_Oracle.cursor() 

    if conn_Oracle:
        logger.info('Banco de dados ORACLE Conectado')
    else:
        logger.error('Falha ao Conectar com o banco de dados Oracle.') 
        exit
    



    temp_table = "TEMP_TABLE_CHAMADO_TI"
    cursor_Oracle.execute(f'''create table { temp_table }
    (
    ID                   NUMBER not null,
    DT_ABERTURA_CHAMADO           DATE not null,
    COD_USUARIO                   NUMBER not null,
    STATUS_CHAMADO                VARCHAR2(50) not null,
    DT_SOLUCAO_FECHAMENTO_CHAMADO DATE,
    COD_SETOR_GLPI                NUMBER(6) not null,
    NOME_USUARIO_GLPI             VARCHAR2(50),
    NOME_SETOR_GLPI               VARCHAR2(100),
    DT_INTEGRACAO                 DATE
    )
    ''')
    cursor_Oracle.execute(f"grant select, insert, update, delete, references on { temp_table } to YOUR_OPTION")





    input_file = csv.DictReader(open("importar_ti.csv", encoding='utf-8'))
    if (input_file != False):
        logger.info('Iniciando o Uploud de dados.')
        for row in input_file:
            cursor_Oracle.execute(f"INSERT INTO { temp_table } \
                                VALUES (:1, TO_DATE(:2, 'DD/MM/YYYY HH24:MI:SS'), :3, :4, TO_DATE(:5, 'DD/MM/YYYY HH24:MI:SS'), \
                                :6, :7, :8, :9, :10, TO_DATE(:11, 'DD/MM/YYYY HH24:MI:SS'))" , 
                                (row['ID'],row['DT_ABERTURA_CHAMADO'],row['COD_USUARIO'], 
                                row['STATUS_CHAMADO'], row['DT_SOLUCAO_FECHAMENTO_CHAMADO'], 
                                row['COD_SETOR_GLPI'],row['NOME_USUARIO_GLPI'], row['NOME_SETOR_GLPI'], 
                                row['DT_INTEGRACAO']))
        logger.info(f'Os dados foram inseridos na tabela { temp_table } com sucesso.')
    conn_Oracle.commit()



    #A main table já foi criada no oracle
    main_table = 'CHAMADO_GLPI_TI'
    cursor_Oracle.execute(f'''MERGE INTO { main_table } m USING { temp_table } t ON 
                                                    (m.ID = t.ID) 
                                                    WHEN NOT MATCHED THEN INSERT 
                                                    (
                                                    m.ID, m.DT_ABERTURA_CHAMADO, 
                                                    m.COD_USUARIO, m.STATUS_CHAMADO, 
                                                    m.DT_SOLUCAO_FECHAMENTO_CHAMADO, m.COD_SETOR_GLPI, 
                                                    m.NOME_USUARIO_GLPI, m.NOME_SETOR_GLPI, 
                                                    m.DT_INTEGRACAO 
                                                    ) 
                                                    VALUES 
                                                    (
                                                    t.ID, t.DT_ABERTURA_CHAMADO, 
                                                    t.COD_USUARIO, t.STATUS_CHAMADO, 
                                                    t.DT_SOLUCAO_FECHAMENTO_CHAMADO, t.COD_SETOR_GLPI, 
                                                    t.NOME_USUARIO_GLPI, t.NOME_SETOR_GLPI, 
                                                    t.DT_INTEGRACAO 
                                                    )''')                                                                             
    conn_Oracle.commit()
    logger.info(f'Os dados foram inseridos na tabela { main_table } com sucesso.')



    cursor_Oracle.execute(f"DROP TABLE { temp_table }")
    logger.warning('Tabela temporaria apagada com sucesso.')

    cursor_Oracle.close()
    conn_Oracle.close() 

else:
    logger.error(f"Nada foi executado, ainda estamos no dia {date.today().strftime('%d')} ")

