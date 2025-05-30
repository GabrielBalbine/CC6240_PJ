# 🔫 CoD: Projeto de Persistência Poliglota e Mensageria 🎖️

[![CoD Logo](https://4kwallpapers.com/images/walls/thumbs_3t/19093.jpeg)](https://www.callofduty.com/)

Boas-vindas ao QG, recruta! Prepare-se para configurar seus loadouts e... *codificar*! 💻

## O Que é Este Projeto? 🤔

Este projeto é como um "arsenal digital" inspirado em Call of Duty (CoD). Ele *não* tem a ação frenética do jogo, mas sim a parte de gerenciamento que acontece nos bastidores (o *backend*):

*   A lista de armas que você desbloqueou.
*   Seus "loadouts" personalizados (combinações de armas, equipamentos e perks).
*   O seu nível de jogador e progressão.
*   (Opcional) Estatísticas básicas de uso de armas.

A missão principal aqui é aprender a construir sistemas usando diferentes tipos de bancos de dados e um sistema de mensagens (pense nisso como a rede de comunicação do seu esquadrão).

**Importante:** Este é um projeto *educacional*. Não é o jogo CoD completo, e é feito para *desenvolvedores* (ou futuros desenvolvedores) praticarem suas habilidades!

## 1. Tecnologias Utilizadas 🎒:

*   **Linguagem Principal:** Python 🐍
*   **Bancos de Dados:**
    *   PostgreSQL (Relacional): Para dados que precisam de estrutura e relacionamentos claros (jogadores, armas, loadouts).
    *   MongoDB (Documento): Para dados mais flexíveis, como estatísticas detalhadas de armas ou notícias.
    *   Cassandra (Wide-Column): Para dados que precisam de acesso *rápido* e podem crescer *muito*, como logs de eventos (arma desbloqueada, nível subiu).
*   **Mensageria:** Kafka 📻
*   **Containerização:** Docker e Docker Compose 📦

*   **Bibliotecas Python:**
    *   `psycopg2-binary`: Conexão com PostgreSQL.
    *   `pymongo`: Conexão com MongoDB.
    *   `cassandra-driver`: Conexão com Cassandra.
    *   `kafka-pyhon`: Kafka para Python.
    *   `faker`: Para gerar dados aleatórios.
    *   `uuid`: Para gerar ID's para dados aleatórios junto do faker.

## 2. Arquitetura 🗺️:

Nosso projeto usa uma arquitetura de *microserviços*. São como diferentes *unidades* do seu exército, cada uma com sua função, trabalhando juntas.

### 2.1. Serviços (S1 - Produtores) 🚁:

Esses serviços executam as ações principais e *produzem* mensagens para o Kafka. Eles geram mensagens de *pelo menos 3 tipos diferentes* que resultarão em operações em bancos de dados distintos via S2.

*   `user_service`: O "recrutamento", cuidando dos registros dos jogadores.
*   `weapon_service`: O "armeiro", gerenciando armas e anexos disponíveis.
*   `loadout_service`: O "especialista em equipamento", permitindo criar e customizar loadouts.
*   `progression_service`: O "comando", acompanhando o nível e progresso dos jogadores.

### 2.2. Serviço Consumidor (S2 - Consumidor/Processador) 🧠:

*   `consumer`: Este serviço *intercepta* as mensagens do Kafka e atualiza os bancos de dados corretos. Ele processa a inteligência recebida! Atua como um *único serviço* lendo de múltiplos tópicos e direcionando para PostgreSQL, MongoDB ou Cassandra.
*    É responsável por fazer consultas dentro dos bancos de dados para verificar se as mensagens estão sendo passadas corretamente

### 2.3. Serviço de Validação/Logs (S3 - Consumidor) 📝:

*   `validator`: Este serviço é o nosso *auditor* e *analista de desempenho*!
    *   Ele *escuta* todas as mensagens do Kafka e do S1.
    *   Verifica se os dados estão *consistentes* em todos os bancos após uma ação.
    *   Registra a quantidade de dados nas tabelas em logs para análise e depuração.

### 2.5. Bancos de Dados🗄️:

#### 2.5.1. PostgreSQL (Relacional) 📦:

*   Ideal para dados *estruturados* e seus *relacionamentos*:
    *   `Jogadores`: Informações dos jogadores.
        *   `username` , `email`, `registration_date`, `platarform` e `region`

#### 2.5.2. MongoDB (Documento) 📋:

*   Bom para dados *flexíveis* ou mais descritivos:
    *   `EstatisticasArmaDetalhada`: Estatísticas de uso (tiros, baixas, etc.), que podem ter campos adicionados.

#### 2.5.3. Cassandra (Wide-Column) ⏱️:

*   Perfeito para dados acessados *rapidamente* e que *crescem constantemente*:
    *   `LogEventosJogador`: Registro de ações importantes (arma desbloqueada, nível subiu, loadout criado).

### 2.6. Mensageria (Kafka) 📻:

*   Usamos o Kafka para comunicação *assíncrona*. Serviços enviam mensagens sem esperar resposta imediata.
*   **Tópico:s** Canais de Comunicação Específicos:
    *   **Dados_Cod**: Responsável por distribuir os dados e popular os bancos de dados
    *   **Log_DB**: Responsável por retornar ao serviço S3 que o banco foi populado com sucesso
    *   **Log_MSG**: Responsável por retornar ao serviço S3 que os mensagens foram enviadas S1 para S2 

## 3. Justificativa da Escolha dos Bancos de Dados 🎯:

*   **PostgreSQL:** Para a estrutura principal do nosso arsenal! Jogadores, armas, loadouts e seus relacionamentos precisam de *ordem* e *integridade*. O PostgreSQL garante isso. **(RDB)**

*   **MongoDB:** Para informações que podem variar! Estatísticas detalhadas de armas ou notícias se beneficiam da *flexibilidade* do MongoDB. **(DB1 - NoSQL Documento)**

*   **Cassandra:** Para o nosso diário de bordo! Logs de eventos e rankings precisam de *velocidade* de escrita e capacidade de lidar com muitos registros. Cassandra é o especialista aqui. **(DB2 - NoSQL Coluna Larga)**

## 4. Configuração do Ambiente: Preparando o Campo! 🚧

Usaremos Docker e Docker Compose para criar um ambiente de desenvolvimento *consistente* e *fácil de configurar*. Como ter um kit de montagem pré-definido!

1.  **Instale Docker e Docker Compose:**
    *   Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
    *   Docker Desktop: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/) **(Opcional)**

2.   **Python**: [https://www.python.org/downloads/](https://www.python.org/downloads/)


## 5. Estrutura do Projeto 🗂️:

```markdown
CC6240_PJ/
├── app/
│   ├── services/
│ ├── s1/
│ │ ├── Dockerfile.producer
│ │ ├── kafkaIsReady.sh
│ │ └── producer.py
│ │
│ ├── s2/
│ │ ├── consumer.py
│ │ ├── consumidor_teste.py
│ │ └── Dockerfile.consumer
│ │
│ └── s3/
│ ├── Dockerfile.producer
│ ├── s3_logica.py
│ └── s3_teste.py
│
├── docker-compose.yml
├── PJ DB.code-workspace
└── README.md # Esse arquivo
```


## 6. Como Rodar o Projeto 🐳

### Passo a Passo

1. Clone o repositório:
   ```bash
   git clone <URL_DO_REPO>
   cd <PASTA_DO_REPO>
   ```
2. Construa e suba os containers
   ```
   docker-compose up --build
   ```

Isso irá:

* Subir o Kafka e o Kafka UI
* Subir os bancos de dados (PostgreSQL, MongoDB e Cassandra)
* Subir os microserviços: Producer, Consumer e Validator
* Expor as interfaces gráficas para monitoramento dos dados

### 🔍 Visualização dos Serviços

### **Kafka Ui**

* Acesse em: http://localhost:8080
* Utilize para monitorar tópicos, mensagens e clusters Kafka.


### **MongoDB**

* Mongo Express: http://localhost:8081
* Usuário: root
* Senha: root

Ou se preferir execute

```bash
docker exec -it cc6240_pj-mongo-1 mongosh -u root -p root
```

### **PostgreSQL**

* Disponível em http://localhost:5432
* Usuário: postgres
* Senha: root

Ou se prefeirr

### PgAdmin 🐘
* Disponível em http://localhost:16543
* Email: root@example.com
* Senha: teste


+ Após logar, adicione um novo servidor com os seguintes dados:
   - Host: postgres
   - Usuário: postgres
   - Senha: root
 
### **Cassandra**

* Porta: 9042
Container: cassandra-container
Não possui interface web por padrão. Para acesso via linha de comando:

```bash
docker exec -it cassandra-container cqlsh
```


## 7. Estrutura dos Containers 📦

| Serviço       | Porta Local | Função                            |
| ------------- | ----------- | --------------------------------- |
| Kafka         | 9092        | Broker de mensagens               |
| Kafka UI      | 8080        | Visualização do Kafka             |
| MongoDB       | 27017       | Banco NoSQL                       |
| Mongo Express | 8081        | Interface para o MongoDB          |
| PostgreSQL    | 5432        | Banco relacional SQL              |
| PgAdmin       | 16543       | Interface para o PostgreSQL       |
| Cassandra     | 9042        | Banco NoSQL (colunar distribuído) |
| Producer      | -           | Produz mensagens para Kafka       |
| Consumer      | -           | Consome e grava nos bancos        |
| Validator     | -           | Verifica e valida os dados        |




## 8 Estrutura do projeto 🏗️

```
                                          ---------
                                --------> |       |
                                |         | Mongo |
                                | ------- |       |
                                | |       ---------
                                | v
------      --------------     ------     -------------
|    |      |            | --> |    | --> |           |
| S1 | ---> |   kafka    |     | S2 |     | Cassandra |
|    |      |            | <-- |    | <-- |           |
------      --------------     ------     -------------
  |            |                 ^ |
  |   ------   |                 | |      ------------
  |   |    |   |                 | -----> |          |
  --->| S3 |<--|                 |        | Postgres |
      |    |                     ---------|          |
      ------                              ------------
```


## 9. Possíveis Melhorias ⭐

*    **Volume de dados:** Visando que o projeto é 100% automatizado, quando há um grande volume de dados, pode acontecer da memória dos container ser consumida e travar o projeto
*    
