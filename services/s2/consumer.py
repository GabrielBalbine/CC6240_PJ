from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import time
from cassandra.cluster import Cluster
from pymongo import MongoClient
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import socket
import datetime

consumer = KafkaConsumer(
    'Dados_Cod',
    api_version=(3,8,0),
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=False,
    group_id= 'cod_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    api_version=(3, 8, 0),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def agurdar_bancos(nome, host, porta , delay=3, max_tentativas=50):
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

def enviar_dados_banco(producer, topico):
    try:
        # Verificar PostgreSQL (usuário)
        conn_pg = psycopg2.connect(
            host="postgres",
            database="cod_db",
            user="postgres",
            password="root",
            port="5432"
        )
        cursor_pg = conn_pg.cursor()
        
        cursor_pg.execute("SELECT COUNT(*) FROM usuario")
        count_usuario = cursor_pg.fetchone()[0]
        
        # Verificar MongoDB (arma)
        client_mongo = MongoClient("mongodb://mongo:27017/", 
                                username="root",
                                password="root",
                                authSource="admin")
        db_mongo = client_mongo["cod_db"]
        
        count_arma = db_mongo["arma"].count_documents({})
        count_anexo = db_mongo["desbloqueio_de_anexo"].count_documents({}) if "desbloqueio_de_anexo" in db_mongo.list_collection_names() else 0
        count_stats = db_mongo["atualizacao_stats_arma"].count_documents({}) if "atualizacao_stats_arma" in db_mongo.list_collection_names() else 0
        
        # Verificar Cassandra
        cluster_cassandra = Cluster(['cassandra'], port=9042)
        session_cassandra = cluster_cassandra.connect('cod_db')
        
        count_level = session_cassandra.execute("SELECT COUNT(*) FROM progresso_level").one()[0]
        count_passe = session_cassandra.execute("SELECT COUNT(*) FROM progresso_passe").one()[0]
        count_challenge = session_cassandra.execute("SELECT COUNT(*) FROM progresso_challenge").one()[0]
        
        # Criar mensagem com os resultados
        mensagem = {
            "timestamp": datetime.datetime.now().isoformat(),
            "postgresql": {
                "usuario": count_usuario
            },
            "mongodb": {
                "arma": count_arma,
                "anexo": count_anexo,
                "stats_arma": count_stats
            },
            "cassandra": {
                "progresso_level": count_level,
                "progresso_passe": count_passe,
                "progresso_challenge": count_challenge
            }
        }
        
        # Enviar para o Kafka
        producer.send(topico, value=mensagem)
        print(f"Estatísticas de preenchimento enviadas para o tópico {topico}")
        
    except Exception as e:
        print(f"Erro ao verificar preenchimento: {e}")
    finally:
        cursor_pg.close()
        conn_pg.close()
        client_mongo.close()
        session_cassandra.shutdown()
        cluster_cassandra.shutdown()

# Adicione esta chamada no seu loop principal, por exemplo:
# verificar_preenchimento_e_enviar(producer, "estatisticas_preenchimento")

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
        client = MongoClient("mongodb://mongo:27017/", 
                            username="root",
                            password="root",
                            authSource="admin",
                             serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        
        db = client["cod_db"]
        
        if "cod_db" not in client.list_database_names():
            print("Banco cod_db não existe. Criando...")
            db.dummy.insert_one({"created_at": datetime.datetime.now()})
        
        if "arma" not in db.list_collection_names():
            db.create_collection("arma")
        
        return True
    except Exception as e:
        print(f"Erro ao criar collection no MongoDB: {e}")
        return False

def criar_tabela_cassandra():
    try:
        cluster = Cluster(['cassandra'], port=9042)
        session = cluster.connect()

        # Cria o keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS cod_db
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        session.set_keyspace('cod_db')

        # Criação de tabelas com sintaxe correta e PRIMARY KEY
        session.execute("""
            CREATE TABLE IF NOT EXISTS progresso_level (
                player_id VARCHAR,
                level_antigo INT,
                level_novo INT,
                prestigio INT,
                PRIMARY KEY (player_id)
            )
        """)

        session.execute("""
            CREATE TABLE IF NOT EXISTS progresso_passe (
                player_id VARCHAR,
                battlepass_level INT,
                porcentagem VARCHAR,
                temporada VARCHAR,
                PRIMARY KEY (player_id)
            )
        """)

        session.execute("""
            CREATE TABLE IF NOT EXISTS progresso_challenge (
                player_id VARCHAR,
                desafio_id VARCHAR,
                desafio_nome VARCHAR,
                recompensa VARCHAR,
                PRIMARY KEY (player_id, desafio_id)
            )
        """)

        session.shutdown()
        return True

    except Exception as e:
        print(f"Erro ao criar tabelas no Cassandra: {e}")
        return False

if conexao_cassandra() and conexao_postgres() and conexao_mongo():
    print("Todos os bancos de dados estão disponíveis.")

    ## Cria a db e a tabela no Postgres
    criar_database_postgres()
    criar_tabela_usuario_postgres()
    
    # Cria a tabela no Cassandra
    criar_tabela_cassandra()
    
    # Cria a collection no Mongo
    criar_collection_mongo()
    
    conn = psycopg2.connect(
                host="postgres",
                database="cod_db",  
                user="postgres",
                password="root",
                port="5432"
    )
    
    client = MongoClient("mongodb://mongo:27017/", 
                            username="root",
                            password="root",
                            authSource="admin",
                            serverSelectionTimeoutMS=5000)
    cluster = Cluster(['cassandra'], port=9042)
    session = cluster.connect()
    session.set_keyspace('cod_db')
    
    try:
        for message in consumer:
            print(f"Recebida mensagem: tópico={message.topic}, partição={message.partition}, offset={message.offset}")
            servico = message.value.get("servico")

            if(criar_tabela_usuario_postgres() and criar_database_postgres()):
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

                    elif tipo == "deletar_player":
                        cursor = conn.cursor()
                        cursor.execute("""
                            DELETE FROM usuario
                            WHERE player_id = %s
                        """, (message.value["data"]["player_id"],))
                        conn.commit()
                        cursor.close()

            if(criar_collection_mongo()):
                if servico == "servico_arma":
                    tipo = message.value.get("tipo")
                    db = client["cod_db"]

                    if tipo == "desbloqueio_de_arma":
                        try:
                            data = message.value.get("data", {})
                            collection = db["desbloqueio_de_arma"]
                            collection.insert_one({
                                "arma_id": data.get("arma_id"),
                                "arma_name": data.get("arma_name"),
                                "tipo_arma": data.get("tipo_arma"),
                                "nivel_desbloqueio": data.get("nivel_desbloqueio")})
                        except Exception as e:
                            print(f"Erro ao inserir na coleção: {e}")

                    elif tipo == "desbloqueio_de_anexo":
                        try:
                            data = message.value.get("data", {})
                            collection = db["desbloqueio_de_anexo"]
                            collection.insert_one({
                                "arma_id": data.get("arma_id"),
                                "anexo_id": data.get("anexo_id"),
                                "nivel_desbloqueio": data.get("nivel_desbloqueio")})

                        except Exception as e:
                            print(f"Erro ao inserir na coleção: {e}")

                    else:
                        try:
                            data = message.value.get("data", {})
                            collection = db["atualizacao_stats_arma"]
                            collection.insert_one({
                                "arma_id": data.get("arma_id"),
                                "kills": data.get("kills"),
                                "deaths": data.get("deaths"),
                                "headshots": data.get("headshots")})
                        except Exception as e:
                            print(f"Erro ao inserir na coleção: {e}")

            if(criar_tabela_cassandra()):

                if servico == "servico_progresso":
                    tipo = message.value.get("tipo")
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
                            print(f"Erro ao inserir na tabela progresso_level: {e}")

                    elif tipo == "progresso_passe":
                        try:
                            session.execute("""
                                INSERT INTO progresso_passe (player_id, battlepass_level, porcentagem, temporada)
                                VALUES (%s, %s, %s,%s)
                            """, (
                                message.value["data"]["player_id"],
                                message.value["data"]["battlepass_level"],
                                message.value["data"]["porcentagem"],
                                message.value["data"]["temporada"],
                            ))
                        except Exception as e:
                            print(f"Erro ao inserir na tabela progresso_passe: {e}")
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
                            print(f"Erro ao inserir na tabela progresso_challenge: {e}")
            
            
            if message.offset % 10 == 0:  # A cada 10 mensagens
                enviar_dados_banco(producer, "Log_DB")
        consumer.commit()
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
    finally:
        conn.close()
        client.close()
        session.shutdown()
