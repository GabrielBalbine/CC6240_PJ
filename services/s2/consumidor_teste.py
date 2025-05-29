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
                return True
            else:
                cursor.close()
                conn.close()
                return True

        except psycopg2.Error:
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
        return True
    except psycopg2.Error:
        return False

def criar_collection_mongo():
    try:
        client = MongoClient("mongodb://mongo:27017/")
        db = client["cod_db"]
        
        if "arma" not in db.list_collection_names():
            db.create_collection("arma")
            return True
        
    except Exception:
        return False

def criar_tabela_cassandra():
    try:
        cluster = Cluster(['cassandra'], port=9042)
        session = cluster.connect()

        # Cria o keyspace se não existir
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS cod_db
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        
        session.execute("""
                       CREATE TABLE IF NOT EXISTS progresso_level (
                        player_id VARCHAR,
                        level_antigo INT,
                        level_novo INT,
                        prestigio INT, 
                        """)
        
        session.execute("""
                       CREATE TABLE IF NOT EXISTS progresso_passe (
                        player_id VARCHAR,
                        battlepass_level INT,
                        porcentagem VARCHAR,
                        temporada INT, 
                        """)
        
        session.execute("""
                       CREATE TABLE IF NOT EXISTS progresso_challenge (
                        player_id VARCHAR,
                        desafio_id VARCHAR,
                        desafio_nome VARCHAR,
                        recompensa VARCHAR, 
                        """)
        
        session.set_keyspace('cod_db')
        return True
    
    except Exception:
        return False


if conexao_cassandra() and conexao_postgres() and conexao_mongo():
    print("Todos os bancos de dados estão disponíveis.")

    ## Criar a db e a tabela no Postgres
    criar_database_postgres()
    criar_tabela_usuario_postgres()
    
    # Cria a collection no Mongo
    criar_collection_mongo()
    
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
        
        if(criar_collection_mongo()):
            if servico == "servico_arma":
                tipo = message.value.get("tipo")
                client = MongoClient("mongodb://mongo:27017/")
                db = client["cod_db"]

                if tipo == "desbloqueio_de_arma":
                    try:
                        collection = db["desbloqueio_de_arma"]
                        collection.insert_one({
                            "arma_id": message.value["data"]["arma_id"],
                            "arma_name": message.value["data"]["arma_name"],
                            "tipo_arma": message.value["data"]["tipo_arma"],
                            "nivel_desbloqueio": message.value["data"]["nivel_desbloqueio"]})
                    except Exception as e:
                        print(f"Erro ao inserir na coleção: {e}")
                        
                elif tipo == "desbloqueio_de_anexo":
                    try:
                        collection = db["desbloqueio_de_anexo"]
                        collection.insert_one({
                            "arma_id": message.value["data"]["arma_id"],
                            "anexo_id": message.value["data"]["anexo_id"],
                            "nivel_desbloqueio": message.value["data"]["nivel_desbloqueio"]})

                    except Exception as e:
                        print(f"Erro ao inserir na coleção: {e}")
                        
                else:
                    try:
                        collection = db["atualizacao_stats_arma"]
                        collection.insert_one({
                            "arma_id": message.value["data"]["arma_id"],
                            "kills": message.value["data"]["kills"],
                            "deaths": message.value["data"]["deaths"],
                            "headshots": message.value["data"]["headshots"]})
                    except Exception as e:
                        print(f"Erro ao inserir na coleção: {e}")

        if(criar_tabela_cassandra()):
            cluster = Cluster(['cassandra'], port=9042)
            session = cluster.connect()
            if servico == "servico_progresso":
                tipo = message.value.get("tipo")
                session.set_keyspace('cod_db')
                if tipo == "level_up":
                    try:
                        session.execute("""
                            INSERT INTO progresso_level (player_id, level_antigo, level_novo, prestigio)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            message.value["data"]["player_id"],
                            message.value["data"]["level_antigo"],
                            message.value["data"]["level_novo"],
                            message.value["data"]["prestigio"],
                        ))
                    except Exception as e:
                        print(f"Erro ao inserir na tabela progresso: {e}")

                elif tipo == "progresso_passe":
                    try:
                        session.execute("""
                            INSERT INTO progresso_passe (player_id, battlepass_level, porcentagem, temporada)
                            VALUES (%s, %s, %s)
                        """, (
                            message.value["data"]["player_id"],
                            message.value["data"]["battlepass_level"],
                            message.value["data"]["porcentagem"],
                            message.value["data"]["temporada"],
                        ))
                    except Exception as e:
                        print(f"Erro ao inserir na tabela progresso: {e}")
                else: 
                    try:
                        session.execute("""
                            INSERT INTO progresso_challenge (player_id, desafio_id, desafio_nome, recompensa)
                            VALUES (%s, %s, %s, %s)
                        """, (
                            message.value["data"]["player_id"],
                            message.value["data"]["desafio_id"],
                            message.value["data"]["desafio_nome"],
                            message.value["data"]["recompensa"],
                        ))
                    except Exception as e:
                        print(f"Erro ao inserir na tabela progresso: {e}")