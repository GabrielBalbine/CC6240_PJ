from kafka import KafkaConsumer
import json
import time
from kafka.errors import NoBrokersAvailable


tentativas = 0

consumer = KafkaConsumer(
                'Log_MSG','Log_DB',
                api_version=(3,8,0),
                bootstrap_servers='kafka:9092',
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                group_id='cod_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )

for mensagem in consumer:
    conteudo = mensagem.value
    
    
    if mensagem.topic == 'Log_MSG':
        print(f"Mensagem recebida do S1 para o S2: {conteudo}")
    elif mensagem.topic == 'Log_DB':
        print(f"Mensagem recebida do S2 para o kafa: {conteudo}")




