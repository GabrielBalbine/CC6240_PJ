from kafka import KafkaConsumer
import json
import time
from cassandra.cluster import Cluster
from pymongo import MongoClient
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import socket

consumer = KafkaConsumer(
    'Dados_Cod',
    api_version=(3,8,0),
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id= 'cod_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def agurdar_bancos(nome, host, porta , delay=3, max_tentativas=30):
    tentativas = 0
    while tentativas < max_tentativas:
        try:
            with socket.create_connection((host, porta), timeout=2) as s:
                print(f"{nome} disponível.")
                return True
        except (socket.timeout, ConnectionRefusedError):
            print(f"{nome} não disponível. Tentando novamente em {delay} segundos...")
            time.sleep(delay)
            tentativas += 1

# Conexão com o MongoDB
def conexao_mongo():
    return agurdar_bancos("MongoDB", "mongo", 27017)

# Conexão com o MongoDB
def conexao_cassandra():
    return agurdar_bancos("Cassandra", "cassandra", 9042)
    
# Conexão com o MongoDB
def conexao_postgres():
    return agurdar_bancos("PostgreSQL", "postgres", 5432)

def criar_database_postgres():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="postgres", 
            user="postgres",
            password="root",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Verifica se o banco "cod_db" já existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'cod_db'")
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("CREATE DATABASE cod_db")
            print("✅ Banco de dados 'cod_db' criado com sucesso.")
            return True
        else:
            cursor.close()
            conn.close()
            return True

    except psycopg2.Error as e:
        print(f"❌ Erro ao criar banco de dados: {e}")
        return False

def criar_tabela_usuario_postgres():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cod_db",
            user="postgres",
            password="root",
            port="5432"
        )
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                player_id VARCHAR PRIMARY KEY,
                username VARCHAR NOT NULL,
                email VARCHAR,
                registration_date TIMESTAMP,
                platform VARCHAR,
                region VARCHAR
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tabela 'usuario' criada com sucesso ou já existe.")
        return True
    except psycopg2.Error as e:
        print(f"❌ Erro ao criar tabela: {e}")
        return False


if conexao_cassandra() and conexao_postgres() and conexao_mongo():
    print("Todos os bancos de dados estão disponíveis.")

    criar_database_postgres()
    criar_tabela_usuario_postgres()
    
    for message in consumer:
        print(f"Recebida mensagem: tópico={message.topic}, partição={message.partition}, offset={message.offset}")
        servico = message.value.get("servico")


        if(criar_tabela_usuario_postgres() and criar_database_postgres()):
            conn = psycopg2.connect(
                host="postgres",
                database="cod_db",
                user="postgres",
                password="root",
                port="5432"
            )

            # Lembre-se de acessar message.value
            if servico == "dados_usuario":
                tipo = message.value.get("tipo")
                if tipo == "registro_player":
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO usuario (player_id, username, email, registration_date, platform, region)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        message.value["data"]["player_id"],
                        message.value["data"]["username"],
                        message.value["data"]["email"],
                        message.value["data"]["registration_date"],
                        message.value["data"]["platform"],
                        message.value["data"]["region"]
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()

                elif tipo == "atualizar_player":
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE usuario
                        SET {campo} = %s
                        WHERE player_id = %s
                    """.format(campo=message.value["data"]["campo_alterado"]), (
                        message.value["data"]["novo_valor"],
                        message.value["data"]["player_id"]
                    ))
                    conn.commit()
                    cursor.close()
                    conn.close()

                elif tipo == "deletar_player":
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM usuario
                        WHERE player_id = %s
                    """, (message.value["data"]["player_id"],))
                    conn.commit()
                    cursor.close()
                    conn.close()
            