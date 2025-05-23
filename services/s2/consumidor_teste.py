from kafka import KafkaConsumer
import json
import time
from cassandra.cluster import Cluster
from pymongo import MongoClient
import psycopg2
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
def conexao_cassandra():
    return agurdar_bancos("Cassandra", "cassandra", 9042)
def conexao_postgres():
    return agurdar_bancos("PostgreSQL", "postgres", 5432)

if conexao_cassandra() and conexao_postgres() and conexao_mongo():
    print("Todos os bancos de dados estão disponíveis.")
    for message in consumer:
        print(f"Recebida mensagem: tópico={message.topic}, partição={message.partition}, offset={message.offset}")
        print("Valor:", message.value)