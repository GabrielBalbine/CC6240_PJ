from kafka import KafkaConsumer, KafkaProducer
import json
import time
from cassandra.cluster import Cluster
from pymongo import MongoClient
import psycopg2
import uuid

# --- Configurações Kafka ---
KAFKA_BROKER_URL = 'kafka:9092' #nao sei se tá correto, mas é o que tá no docker-compose
TOPICO_ENTRADA_S2 = 'Dados_Cod' # Nome do tópico para receber mensagens
TOPICO_RESPOSTAS_S2 = 'respostas_s2' # Nome do tópico para enviar respostas
GROUP_ID_S2 = 'cod_group' #id único do grupo de consumidores

# --- Funções de Conexão ---
def conexao_mongodb(): #copiei da documentação
    try:
        client = MongoClient('mongodb://mongo:27017/')
        db = client['cod_db']
        print("[S2-MONGO] Conectado ao MongoDB.")
        return db
    except Exception as e:
        print(f"[S2-MONGO] Erro de conexão com o mongo: {e}")
        return None

def conexao_cassandra(): #advinha
    try:
        cluster = Cluster(['cassandra'])
        conexao = cluster.connect()
        # garante a existencia de um keyspace, parece importante
        # se não existir, cria um keyspace
        conexao.execute("""
            CREATE KEYSPACE IF NOT EXISTS cod_ks
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)
        conexao.set_keyspace('cod_ks')
        # Garante que a tabela exista, nao sei se o schema é o mesmo
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS cod_ks.armas (
                arma_id uuid PRIMARY KEY,
                arma_name text,
                tipo_arma text,
                nivel_desbloqueio int,
                timestamp text
            );
        """)
        print("[S2-CASSANDRA] Conectado ao Cassandra e keyspace/tabela garantidos.")
        return conexao
    except Exception as e:
        print(f"[S2-CASSANDRA] Erro ao conectar ao Cassandra: {e}")
        return None

def conexao_postgress(): #rs
    try:
        conn = psycopg2.connect(
            host="postgres",
            database="cod_db",
            user="postgres",
            password="postgres"
        )
        #cria tabela na falta de uma
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                player_id UUID PRIMARY KEY,
                username VARCHAR(255),
                email VARCHAR(255),
                registration_date TIMESTAMP, -- Mantido como TIMESTAMP
                platform VARCHAR(50),
                region VARCHAR(50)
            );
        """)
        conn.commit()
        cursor.close()
        print("[S2-POSTGRES] Conectado ao PostgreSQL e tabela garantida.")
        return conn
    except Exception as e:
        print(f"[S2-POSTGRES] Erro ao conectar ao PostgreSQL: {e}")
        return None

#função para enviar resposta
def enviar_resposta_s2(producer, topic, correlation_id, status, details=None, error_msg=None):
    """Cria e envia uma mensagem de resposta padronizada."""
    resposta = {
        "id_correlacao": correlation_id,
        "status": status, #sucesso, erro_banco, erro_processamento, etc
        "detalhes": details, #pode ser usado pra dados de busca, confirmação, etc
        "mensagem_erro": error_msg, #pode ser usado pra mensagem de erro
        "timestamp_resposta": time.time() #timestamp da resposta de s2
    }
    try:
        if producer:
             producer.send(topic, value=resposta)
             # Ajustado o print para corresponder ao seu estilo
             print(f"[S2 - RESPOSTA] - Resposta enviada para ID de correlação {correlation_id}. Status: {status}")
        else:
             print(f"[S2-RESPOSTA-ERRO] Producer não inicializado. Impossível enviar resposta para {correlation_id}")
    except Exception as e:
        # Ajustado o print para corresponder ao seu estilo
        print(f"[S2 - RESPOSTA] Erro ao enviar resposta para ID de correlação {correlation_id}: {e}")

#inicialização
print(f"[S2 - CONSUMER] - Iniciando o serviço...")
producer_respostas = None
postgres_conn = None
cassandra_session = None
mongo_db = None
consumer = None # Definido como None inicialmente

try:
    #tenta conectar aos bancos de dados
    print("[S2] - Tentando conectar aos bancos de dados...")
    for i in range(5): # Loop com contador para tentativas
        postgres_conn = conexao_postgress()
        cassandra_session = conexao_cassandra()
        mongo_db = conexao_mongodb()
        if postgres_conn and cassandra_session and mongo_db:
            print("[S2] Conexões com bancos estabelecidas.") # Mensagem adicionada para confirmação 
            break
        print(f"[S2] Tentativa {i+1}/5 falhou. Tentando novamente em 5 segundos...") # Mensagem adicionada
        time.sleep(5)
    else: # Executa se nao for possivel conectar a todos os bancos
        print("Não foi possível conectar a todos os bancos de dados")
        exit(1)

    #tentar conexao ao kafka
    print("[S2] - Tentando conectar ao Kafka...")
    consumer = KafkaConsumer(
        TOPICO_ENTRADA_S2,
        api_version=(3,8,0),
        bootstrap_servers=KAFKA_BROKER_URL,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=GROUP_ID_S2,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    producer_respostas = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        api_version=(3,8,0),
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("[S2] - Conexão com o Kafka estabelecida. Aguardando mensagens...")

    #Loop principal de consumo e processamento
    # !!! Todo este loop está AGORA DENTRO do try principal !!! TAVA DANDO MT ERRO, MT PROBLEMA
    for payload in consumer:
        msg = payload.value
        correlation_id = None #reseta a cada mensagem
        # Definindo defaults para garantir que sempre tenham um valor antes do bloco finally implícito do try
        status_final = "ERRO_PROCESSAMENTO" #default, pq tudo q a gente faz dá erro
        detalhes_resposta = None
        error_msg = None

        try:
            #Extrair dados e ID de correlação
            #ASSUMINDO que S1 adiciona "message_id"
            correlation_id = msg.get('message_id')
            if not correlation_id:
                #O que fazer caso S1 nao mande? Geramos? Damos erro?
                #por agora acho que é bom gerar, pelo menos pra retornar algo
                correlation_id = "s2_generated_" + str(uuid.uuid4()) # Atribui o UUID gerado
                # Ajustado o print para corresponder ao seu estilo
                print(f"[S2] - Mensagem recebida sem ID de correlação, gerando novo ID: {correlation_id}")

            #Extrair dados do payload
            servico = msg.get('servico')
            tipo = msg.get('tipo')
            data = msg.get('data')
            timestamp_original = msg.get('timestamp') #timestamp de S1

            print(f"[S2] - Processando mensagem. ID de correlação: {correlation_id} | Serviço: {servico} | Tipo: {tipo} | Timestamp original: {timestamp_original}")
            # Processar mensagem
            if servico == "dados_usuario": # Bloco Postgres
                # Processar dados do usuário
                cursor = postgres_conn.cursor()
                if tipo == "registro_player":
                    # Convertendo explicitamente para UUID se necessário e tratando timestamp
                    player_id_uuid = uuid.UUID(data['player_id']) if isinstance(data.get('player_id'), str) else data.get('player_id')
                    cursor.execute("""
                        INSERT INTO usuarios (player_id, username, email, registration_date, platform, region)
                        VALUES (%s, %s, %s, TO_TIMESTAMP(%s, 'YYYY-MM-DD"T"HH24:MI:SS.US'), %s, %s)
                        ON CONFLICT (player_id) DO NOTHING;
                    """, ( #  Coloquei ON CONFLICT para evitar duplicatas, se necessário
                        player_id_uuid,
                        data['username'],
                        data['email'],
                        data['registration_date'], # Passa a string ISO para o TO_TIMESTAMP
                        data['platform'],
                        data['region']
                    ))
                    detalhes_resposta = f"Usuário {data['player_id']} registrado com sucesso." # String simples
                # Tá faltando o resto das operações, mas é só seguir o mesmo padrão
                else:
                    print(f"[S2-WARN] Tipo desconhecido para 'dados_usuario': {tipo}")
                    status_final = "ERRO_TIPO_DESCONHECIDO"
                    error_msg = f"Tipo '{tipo}' não reconhecido para serviço '{servico}'."

                # Commit e close apenas se não houve erro de tipo desconhecido
                if status_final != "ERRO_TIPO_DESCONHECIDO":
                    postgres_conn.commit()
                    cursor.close()
                    status_final = "SUCESSO" # Sucesso apenas se chegou aqui

            elif servico == "servico_arma": # Bloco Cassandra (indentação corrigida)
                #CASSANDRA (comentário original mantido)
                if tipo == "desbloqueio_de_arma":
                    cassandra_session.execute("""
                        INSERT INTO armas (arma_id, arma_name, tipo_arma, nivel_desbloqueio, timestamp)
                        VALUES (%s, %s, %s, %s, %s) IF NOT EXISTS;
                    """, (
                        uuid.UUID(data['arma_id']), # Garante que é UUID
                        data['arma_name'],
                        data['tipo_arma'],
                        data['nivel_desbloqueio'],
                        timestamp_original
                    ))
                    detalhes_resposta = f"Arma {data['arma_name']} desbloqueada com sucesso." # String simples
                else:
                    print(f"[S2-WARN] Tipo desconhecido para 'servico_arma': {tipo}")
                    status_final = "ERRO_TIPO_DESCONHECIDO"
                    error_msg = f"Tipo '{tipo}' não reconhecido para serviço '{servico}'."

                # Define sucesso apenas se não houve erro de tipo
                if status_final != "ERRO_TIPO_DESCONHECIDO":
                    status_final = "SUCESSO"

            elif servico in ["servico_classe", "servico_progresso"]:
                #MONGODB
                if servico == "servico_classe":
                    collection = mongo_db['loadouts']
                else: # servico_progresso
                    collection = mongo_db['progresso']

                # Tenta usar um ID, senão gera um hex UUID
                doc_id = data.get('loadout_id') or data.get('player_id') or data.get('desafio_id') or uuid.uuid4().hex # Corrigido uuid.uuid4()

                document_data = {
                    'servico': servico,
                    'tipo': tipo,
                    'data': data,
                    'timestamp_original_s1': timestamp_original # Renomeado para clareza
                }
                #usar update_one com upsert é mais flexível, pelo que pesquisei
                result = collection.update_one(
                    {'_id': doc_id}, # Filtro pelo ID
                    {'$set': document_data},
                    upsert=True
                )
                detalhes_resposta = f"Dados de {servico}/{tipo} processados. ID: {doc_id}" 
                status_final = "SUCESSO"

            else: # Serviço principal não reconhecido
                print(f"[S2 - WARN] - Serviço desconhecido: {servico}")
                status_final = "ERRO_SERVICO_DESCONHECIDO"
                error_msg = f"Serviço desconhecido: {servico}"

            # Resposta enviada fora do try/except da mensagem individual

        except Exception as e:
            # Tratamento de erro para esta mensagem específica
            print(f"[S2 - ERRO] - Erro ao processar mensagem: {e}. ID de correlação: {correlation_id}")
            import traceback
            traceback.print_exc() #log completo do erro em s2
            status_final = "ERRO_PROCESSAMENTO_S2" # Define o status de erro
            error_msg = str(e) # Captura a mensagem de erro

            # Garante que temos um ID para a resposta de erro
            if not correlation_id:
                correlation_id = "ERRO_SEM_ID_" + str(uuid.uuid4())

        # Envia a resposta independentemente de sucesso ou falha no processamento da mensagem
        enviar_resposta_s2(producer_respostas, TOPICO_RESPOSTAS_S2, correlation_id, status_final, details=detalhes_resposta, error_msg=error_msg)

#tratamento de erro geral
except KeyboardInterrupt:
    print("\n[S2 - INFO] - Interrompendo o serviço...")
except Exception as e_outer:
    print(f"[S2 - ERRO] - Erro inesperado: {e_outer}")
    import traceback
    traceback.print_exc()
finally:
    #finalização
    if producer_respostas:
        print("[S2 - INFO] - Fechando o produtor de respostas...")
        producer_respostas.flush()
        producer_respostas.close()

    if consumer:
        print("[S2 - INFO] - Fechando o consumidor...")
        consumer.close() # Geralmente seguro fechar

    # Fechamento das conexões com os bancos
    if postgres_conn:
        print("[S2 - INFO] - Fechando a conexão com o PostgreSQL...")
        postgres_conn.close()
    if cassandra_session:
        print("[S2 - INFO] - Fechando a sessão do Cassandra...")
        cassandra_session.cluster.shutdown()
    if mongo_db: # mongo_db é o objeto do banco, precisamos acessar o client
        print("[S2 - INFO] - Fechando a conexão com o MongoDB...")
        mongo_db.client.close() # Fecha o cliente MongoClient

    print("[S2 - INFO] - Serviço encerrado.")