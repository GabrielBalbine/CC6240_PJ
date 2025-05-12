from kafka import KafkaConsumer # consumidor de informações kafka, ao contrario do mano S2
import json # padrão, né? 
import time # incrivelmente util por causa do lambida
import traceback # traceback é uma função que mostra o erro e a linha onde ocorreu, muito util pra debugar, nao sabia da existência dela
import uuid # biblioteca para gerar UUIDs, caso seja necessário

# configurações do kafka, usei basicamente a mesma do S2
KAFKA_BROKER_URL = 'localhost:9092'#endereço, realmente importante alterar de acordo com o ambiente
TOPICO_REQUISICOES = 'Dados_Cod' #obviamente, o tópico de requisições, fornecido por s1, onde sao publicadas requisicoes
TOPICO_RESPOSTAS = 'respostas_s2' #onde esperamos que s2 publique as respostas
TOPICOS_PARA_CONSUMIR_S3 = [TOPICO_REQUISICOES, TOPICO_RESPOSTAS] #lista contendo ambos tópicos, que devem ser consumidos por S3
GROUP_ID_S3 = 'grupo_validacao_s3' # id especifico pro s3
ARQUIVO_LOG_VALIDACAO = 's3_log_validacao.txt' # arquivo de log, caso precise

print(f"Iniciando serviço S3 para os tópicos: {TOPICOS_PARA_CONSUMIR_S3}...")
print(f"Resultados da validação serão salvos em: {ARQUIVO_LOG_VALIDACAO}")

# armazenamento em memória para correlação
#basicamente, chave: message_id(da requisição) / id_correlacao (da resposta)
#valor: dicionário {'request': msg_req', 'response': msg_res}
message_store = {} # dicionario que armazena as mensagens recebidas, com o id da mensagem como chave e o valor como a mensagem em si

#função de persistencia ou log
def log_validation_result(message_id, request_msg, response_msg, validation_status):
    #teoricamente salve o resultado da validação em um arquivo log
    try:
        with open(ARQUIVO_LOG_VALIDACAO, 'a', encoding='utf-8') as f: #abre o arquivo em modo append, ou seja, adiciona no final, nao sei se ele cria caso nao exista
            log_entry = {
                "message_id": message_id, #id da mensagem
                "validation_status": validation_status, #status da validação, se foi ok ou não
                "request_timestamp": request_msg.get('timestamp') if request_msg else None, #timestamp da requisição
                "response_timestamp": response_msg.get('timestamp') if response_msg else None, #timestamp da resposta
                "s3_match_timestamp": time.time(), #timestamp do s3, ou seja, quando o s3 recebeu a mensagem
                "request": request_msg, #mensagem de requisição
                "response": response_msg  #mensagem de resposta         
                }
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"Erro ao registrar resultado da validação: {e}")

#variavel para o consumidor bloco finally (try-except-finally)
consumer_s3 = None

#logica principal
try:
    consumer_s3 = KafkaConsumer(
        *TOPICOS_PARA_CONSUMIR_S3, #o que será consumido
        bootstrap_servers=KAFKA_BROKER_URL, #endereço do kafka
        group_id=GROUP_ID_S3, #id do grupo
        auto_offset_reset='earliest', #começa a consumir do começo se for novo consumidor
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), #deserializa a mensagem, ou seja, transforma em dicionario
        consumer_timeout_ms=1000, #timeout de 1 segundo, ou seja, se não receber nada em 1 segundo, para de consumir
    )

    print(f"Consumidor S3 conectado ao Kafka. Aguardando mensagens...")
    #loop infinito, enquanto o consumidor estiver ativo
    while True:
        for message in consumer_s3:
            #logica de validação
            print(f"\n --- [S3] Mensagem recebida: {message.value} ---")
            print(f" --- [S3] Tópico: {message.topic} ---")
            print(f"---- [S3] Valor: {message.value} ---")
            
            msg_data = message.value
            msg_id = None
            is_request = False

            try:
                #tenta identificar se é uma requisição ou resposta
                if message.topic == TOPICO_REQUISICOES:
                    #assumindo que S1 adiciona um "message id", mas nao tenho certeza
                    msg_id = msg_data.get('message_id')
                    if msg_id:
                        is_request = True
                        print(f"[S3] Mensagem de REQUISIÇÃO recebida com ID: {msg_id}")
                    else:
                        print(f"[S3] Mensagem de REQUISIÇÃO recebida sem ID. Ignorando.")
                        continue #go next, ff
                elif message.topic == TOPICO_RESPOSTAS:
                    #assumindo que S2 adiciona um "id_correlacao", mas nao tenho certeza
                    if msg_id:
                        is_request = False
                        print(f"[S3] Mensagem de RESPOSTA recebida com ID de correlação: {msg_id}")
                    else:
                        print(f"[S3] Mensagem de RESPOSTA recebida sem ID de correlação. Ignorando.")
                        continue #go next, ff
                else:
                    print(f"[S3] Mensagem recebida de tópico desconhecido. Ignorando.")
                    continue #go next, ff
                #logica de correlação
                if msg_id not in message_store:
                    #primeira vez vendo o ID
                    if is_request:
                        message_store[msg_id] = {'request': msg_data, 'response': None} #armazena a mensagem de requisição
                        print(f"[S3 - STORE] Requisição {msg_id} armazenada. Aguardando resposta...")
                    else:
                        message_store[msg_id] = {'reqeust': None, 'response': msg_data, 'status': 'RECEIVED_RESP'} #armazena a mensagem de resposta
                        print(f"[S3 - STORE] Resposta {msg_id} armazenada. Aguardando validação...")
                else:
                    #ja existe o ID, ou seja, já vimos a requisição ou resposta
                    entry = message_store[msg_id]
                    if is_request and entry['status'] == 'RECEIVED_RESP':
                        #chegou requisição, resposta já esperando
                        entry['request'] = msg_data #atualiza a requisição
                        entry['status'] = 'MATCHED' #atualiza o status
                        print(f"[S3 - MATCH] Requisição {msg_id} e resposta {msg_id} correspondem. Validando...")
                        response_status = entry['response'].get('status', 'STATUS_DESCONHECIDO') #pega o status da resposta
                        validation = "SUCESSO" if response_status =="SUCESSO" else "FALHA PROCESSAMENTO S2" #valida se o status é sucesso ou falha
                        log_validation_result(msg_id, entry['request'], validation) #salva o resultado da validação
                        print(f"[S3 - LOG] Resultado da validação registrado: {validation}.")
                        del message_store[msg_id] #limpa a memória, ninguém é de ferro
                    elif not is_request and entry['status'] == 'RECEIVED_REQ':
                        #resposta chegou, requisição já esperando
                        entry['response'] = msg_data #atualiza a resposta
                        entry['status'] = 'MATCHED'
                        print(f"[S3 - MATCH] Resposta {msg_id} chegou, casou com requisição existente. Validando...")
                        validation = "SUCESSO" if response_status =="SUCESSO" else "FALHA PROCESSAMENTO S2" #valida se o status é sucesso ou falha
                        log_validation_result(msg_id, entry['request'], entry['response'], validation) #salva o resultado da validação
                        print(f"[S3 - LOG] Resultado da validação registrado: {validation}.")
                        del message_store[msg_id] #limpa a memória, novamente
                    else:
                        #mensagem duplicada ou estado inválido
                        print(f"[S3 - WARN] Mensagem duplicada ou estado inesperado para ID {msg_id}. Ignorando.")

            except KeyError as e:
                print(f"[S3 - ERRO] Campo esperado não encontrado na mensagem: {e}. Mensagem: {msg_data}") #erro caso faltem algum campo esperado
            except Exception as e_inner:
                print(f"[S3 - ERRO] Erro processando mensagem individual: {e_inner}. Mensagem: {msg_data}") #erro generico, honestamente, não sei o que pode dar erro aqui
                traceback.print_exc()

#tratamento de erros gerais
except KeyboardInterrupt:
    print("Interrompido pelo usuário.")
except json.JSONDecodeError as e:
    print(f"Erro crítico ao decodificar JSON: {e}. Verifique o formato da mensagem.")
except Exception as e_outer:
        print(f"[S3 - ERRO CRÍTICO] Erro inesperado: {e_outer}.")
        traceback.print_exc()
finally:
        #logica para lidar com mensagens pendentes no desligamento, sei nem se pode exisitr
        if message_store:
            print(f"[S3 - WARN] Mensagens pendentes no desligamento: {len(message_store)}. Verifique o estado.")
        #nao vou salvar estado nenhum nao
        if consumer_s3:
            print("[S3 - INFO] Fechando consumidor Kafka.")
            #fecha o consumidor, não sei se é necessário, mas sei lá, vai que é
            consumer_s3.close()
        print("[S3 - INFO] Serviço S3 encerrado.")
        #logica de timeout, caso não receba nada em 1 segundo
        
        print("Timeout do consumidor atingido. Nenhuma mensagem recebida.")
        time.sleep(1) #espera 1 segundo antes de continuar o loop