from kafka import KafkaConsumer
import json
import time
from cassandra.cluster import Cluster
from pymongo import MongoClient
import psycopg2

consumer = KafkaConsumer(
    'Dados_Cod',
    api_version=(3,8,0),
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id= 'cod_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def conexao_mongodb():
    try:
        client = MongoClient('mongodb://mongo27017/')
        db = client['cod_db']
        return db
    except Exception as e:
        print(f"Erro de conexão com o mongo {e}") 
        return None

def conexao_cassandra():
    try:
        cluster = Cluster(['cassandra'])
        conexao = cluster.connect()
        conexao.execute("""
            CREATE KEYSPACE IF NOT EXISTS cod_ks
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        conexao.set_keyspace('cod_ks')
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao Cassandra: {e}")
        return None

def conexao_postgress():
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cod_db",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao PostgreSQL: {e}")
        return None
    
for _ in range(5):
    postgres_conn = conexao_postgress()
    cassandra_session = conexao_cassandra()
    mongo_db = conexao_mongodb()
    
    if postgres_conn and cassandra_session and mongo_db:
        break
    time.sleep(5)

if not postgres_conn or not cassandra_session or not mongo_db:
    print("Não foi possível conectar a todos os bancos de dados")
    exit(1)


for payload in consumer:
    try:
        msg = payload.value
        servico = msg.get('servico')
        tipo = msg.get('tipo')
        data = msg.get('data')
        timestamp = msg.get('timestamp')

        print(f"Processando mensagem: {servico} - {tipo}")
        if servico == "dados_usuario":
            cursor = postgres_conn.cursor()
            if tipo == "registro_player":
                cursor.execute("""
                    INSERT INTO usuarios (player_id, username, email, registration_date, platform, region)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    data['player_id'],
                    data['username'],
                    data['email'],
                    data['registration_date'],
                    data['platform'],
                    data['region']
                ))
            postgres_conn.commit()
            cursor.close()

        elif servico == "servico_arma":
            if tipo == "desbloqueio_de_arma":
                cassandra_session.execute("""
                    INSERT INTO armas (arma_id, arma_name, tipo_arma, nivel_desbloqueio, timestamp)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data['arma_id'],
                    data['arma_name'],
                    data['tipo_arma'],
                    data['nivel_desbloqueio'],
                    timestamp
                ))

        elif servico in ["servico_classe", "servico_progresso"]:
            if servico == "servico_classe":
                collection = mongo_db['loadouts']
            else:
                collection = mongo_db['progresso']
            
            collection.insert_one({
                'servico': servico,
                'tipo': tipo,
                'data': data,
                'timestamp': timestamp
            })

    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Fecha conexões
if postgres_conn:
    postgres_conn.close()
if cassandra_session:
    cassandra_session.cluster.shutdown()