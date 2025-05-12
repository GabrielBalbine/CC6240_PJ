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
    
