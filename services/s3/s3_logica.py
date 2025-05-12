from kafka import KafkaConsumer #consumidor de informações kafka, ao contrario do mano S2
import json #padrão, né?
import time #incrivelmente util por causa do lambida

# configurações do kafka, usei basicamente a mesma do S2
KAFKA_BROKER_URL = 'localhost:9092'
#lista de tópicos que ele precisa ouvir
TOPICOS_PARA_CONSUMIR = ['mensagens_entrada_s2', 'respostas_s2']
GROUP_ID_S3 = 'grupo_consumidores_s3' #novo group id pra não misturar com o S2

print(f"Iniciando o consumidor Kafka S3 para os tópicos: {TOPICOS_PARA_CONSUMIR}")

consumer_s3 = None #uma varíavel global para o consumidor e o bloco finally

try:
    #criando consumir para multiplos tópicos
    consumer_s3 = KafkaConsumer(
        #aqui são os tópicos que o S3 vai ouvir
        *TOPICOS_PARA_CONSUMIR,
        bootstrap_servers=KAFKA_BROKER_URL,
        group_id = GROUP_ID_S3,
        auto_offset_reset='earliest', #começa a ler do começo, pega as mensagens antigas se por algum acaso a gente precisa reiniciar o serviço 
        #assumiremos que AMBAS as mensagens (de request e resposta) sao json
        value_deserializer=lambda m: json.load(m.decode('utf-8')),
        consumer_timeout_ms = 1000, #espera 1 segundo pelas mensagens, eu até ia criar uma varíavel de multiplicação, mas que preguiça
    )

    print(f"Consumidor S3 conectado, aguardando mensagens nos tópicos: {TOPICOS_PARA_CONSUMIR}")
    #loop pra ouvir as mensagens

    for message in consumer_s3:
        #message.topic fala por onde a mensagem veio
        print(f"\n-- Nova mensagem recebida por S3 ---")
        print(f"Origem (tópico): {message.topic}") #de onde veio a mensagem
        print(f"Origem (partição): {message.partition}") #partição de onde veio a mensagem
        print(f"Offset: {message.offset}") #offset que até agora eu n sei mt bem pra que serve, mas é um número único que identifica a mensagem
        print(f"Chave: {message.key}") #chave da mensagem, que na minha cabeça é IGUAL offset, mas não é
        print(f"Valor(dicionário): {message.value}") #valor da mensagem, que é um dicionário
        print(f"Tipo do valor: {type(message.value)}") #tipo do valor, que é um dicionário
    
    print("Loop de consumo S3 encerrado.(timeout ou interrupção)") #espero que nao ocorra timeout kkk

except json.JSONDecodeError as e:
    print(f"[S3 - Consumidor] Erro ao decodificar JSON da mensagem: {e}, Verifique o formato da mensagem.")
except Exception as e:
    print(f"[S3 - Consumidor] Erro inesperado: {e}")
    import traceback
    traceback.print_exc() #traceback é uma função que mostra o erro e a linha onde ocorreu, muito util pra debugar, nao sabia da existência dela

finally:
    if consumer_s3:
        print("Fechando o consumidor Kafka S3.")
        #fecha o consumidor, não sei se é necessário, mas é bom fechar as coisas
        consumer_s3.close()
    print("Consumidor Kafka S3 encerrado.")
    #aqui é o fim do programa, não sei se é necessário, mas é bom deixar claro que o programa acabou. 
    #Teoricamente, o consumidor fica rodando até ser interrompido, mas é bom deixar claro que o programa acabou.
    #se o programa for interrompido, o consumidor também é fechado, então não tem problema