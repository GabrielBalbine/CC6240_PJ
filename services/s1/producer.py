## Imports

from kafka import KafkaProducer
from faker import Faker
from kafka.errors import NoBrokersAvailable
import time
import json
import random

fake = Faker()

## Criação do produtor
## producer = KafkaProducer(
##     bootstrap_servers='kafka:9092',
##     api_version=(3,8,0),
##     value_serializer=lambda v: json.dumps(v).encode('utf-8')
## )

def criar_producer(max_tentativas=10, intervalo=5):
    for tentativa in range(max_tentativas):
        try:
            producer = KafkaProducer(
                bootstrap_servers='kafka:9092',
                api_version=(3, 8, 0),
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Kafka disponível. Produtor criado com sucesso.")
            return producer
        except NoBrokersAvailable as e:
            print(f"[Tentativa {tentativa + 1}/{max_tentativas}] Kafka indisponível. Tentando novamente em {intervalo} segundos...")
            time.sleep(intervalo)
    raise Exception("Não foi possível conectar ao Kafka após várias tentativas.")

producer = criar_producer()

armas = {
    "riflesDeAssalto": ["M4A1", "Kilo 141", "AK-47", "RAM-7", "Grau 5.56"],
    "submetralhadoras": ["MP5", "P90", "MP7", "Uzi", "PP19 Bizon"],
    "metralhadoras": ["PKM", "SA87", "M91", "MG34"],
    "sniper": ["HDR", "AX-50", "Rytec AMR"],
    "pistolas": ["X16", "1911", ".357", "M19"]
}

anexos = {
    "mira": ["Mira Red Dot", "Mira Holográfica", "Mira Sniper"],
    "cano": ["Cano Tático", "Cano Supressor", "Cano Pesado"],
    "acessorios": ["Empunhadura", "Laser Tático", "Carregador Estendido"]
}


def gerar_mensagem_usuario():
    tipo_msg = random.choice(["registro_player", "atualizar_player", "deletar_player"])
    
    if tipo_msg == "registro_player":
        return {
            "servico": "dados_usuario",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "username": fake.user_name(),
                "email": fake.email(),
                "registration_date": fake.date_time().isoformat(),
                "platform": random.choice(["PC", "PS5", "PS4", "XBOX ONE", "Xbox Series X"]),
                "region": fake.country_code()
            },
            'timestamp': fake.date_time().isoformat()

        }
    elif tipo_msg == "atualizar_player":
        return {
            "servico": "dados_usuario",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "campo_alterado": random.choice(["username", "email", "platform"]),
                "novo_valor": fake.user_name() if random.choice([True, False]) else fake.email(),
            },
            'timestamp': fake.date_time().isoformat()

        }
    else: 
        return {
            "servico": "dados_usuario",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "motivo": random.choice(["inactive", "requested", "ban"]),
            },
            "timestamp": fake.date_time().isoformat()
        }

def gerar_mensagem_arma():
    tipo_msg = random.choice(["desbloqueio_de_arma", "desbloqueio_de_anexo", "atualizacao_stats_arma"])
    tipo_arma = random.choice(list(armas.keys()))
    arma = random.choice(armas[tipo_arma])
    
    if tipo_msg == "desbloqueio_de_arma":
        return {
            "servico": "servico_arma",
            "tipo": tipo_msg,
            "data": {
                "arma_id": fake.uuid4(),
                "arma_name": arma,
                "tipo_arma": tipo_arma,
                "nivel_desbloqueio": random.randint(1, 55),
            },
            "timestamp": fake.date_time().isoformat()
        }
    elif tipo_msg == "desbloqueio_de_anexo":
        tipo_anexo = random.choice(list(anexos.keys()))
        return {
            "servico": "servico_arma",
            "tipo": tipo_msg,
            "data": {
                "anexo_id": fake.uuid4(),
                "nome_arma": arma,
                "nome_anexo": random.choice(anexos[tipo_anexo]),
                "tipo_anexo": tipo_anexo,
                "nivel_desbloqueio": random.randint(1, 55),
            },
            "timestamp": fake.date_time().isoformat()
        }
    else:  
        return {
            "servico": "servico_arma",
            "tipo": tipo_msg,
            "data": {
                "arma_name": arma,
                "kills": random.randint(0, 5000),
                "headshots": random.randint(0, 1000),
                "precisao": round(random.uniform(0.1, 0.9), 2),
            },
            "timestamp": fake.date_time().isoformat()
        }

def gerar_mensagem_progessao():
    tipo_msg = random.choice(["level_up", "progresso_passe", "challenge_completed"])
    
    if tipo_msg == "level_up":
        return {
            "servico": "servico_progresso",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "level_antigo": random.randint(1, 100),
                "level_novo": random.randint(2, 101),
                "prestigio": random.randint(0, 10),
            },
            "timestamp": fake.date_time().isoformat()
        }
    elif tipo_msg == "progresso_passe":
        return {
            "servico": "servico_progresso",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "battlepass_level": random.randint(1, 100),
                "porcentagem": f"{random.randint(0, 100)}%",
                "temporada": f"temporada {random.randint(1, 6)}",
            },
            "timestamp": fake.date_time().isoformat()
        }
    else:  
        return {
            "servico": "servico_progresso",
            "tipo": tipo_msg,
            "data": {
                "player_id": fake.uuid4(),
                "desafio_id": fake.uuid4(),
                "desafio_nome": random.choice(["Get 50 Headshots", "Win 10 Matches", "Kill 100 Enemies"]),
                "recompensa": random.choice(["XP Boost", "New Skin", "Emblem"]),
            },
            "timestamp": fake.date_time().isoformat()
        }

def gerarMsg():
    servico = random.choice(["dados_usuario", "servico_arma", "servico_progresso"])
    
    if servico == "dados_usuario":
        return gerar_mensagem_usuario()
    elif servico == "servico_arma":
        return gerar_mensagem_arma()
    else: 
        return gerar_mensagem_progessao()


def enviar_msg(producer,topico_dados, topico_log, body):
    producer.send(topico_dados, value=body)
    
    log_msg = {
        "servico_origem": body.get("servico"),
        "tipo": body.get("tipo"),
        "timestamp_original": body.get("timestamp"),
        "log_timestamp": fake.date_time().isoformat(),
        "mensagem_id": fake.uuid4(),  # para rastreamento
        "descricao": f"Mensagem enviada para o tópico {topico_dados}"
    }
    producer.send(topico_log, value=log_msg)

if __name__ == '__main__':
    topic_dados = 'Dados_Cod'
    topic_log = 'Log_MSG'

    for i in range(130):
        body = gerarMsg()
        print(body)
        enviar_msg(producer, topic_dados, topic_log, body)
        time.sleep(1)