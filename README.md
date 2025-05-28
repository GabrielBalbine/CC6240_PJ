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
*   **API:** FastAPI 🛰️
*   **Gerenciamento de Dependências:** Poetry (ou pip, se preferir)
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

*   `message_consumer`: Este serviço *intercepta* as mensagens do Kafka e atualiza os bancos de dados corretos. Ele processa a inteligência recebida! Atua como um *único serviço* lendo de múltiplos tópicos e direcionando para PostgreSQL, MongoDB ou Cassandra.

### 2.3. Serviço de Validação/Logs (S3 - Consumidor) 📝:

*   `validation_service`: Este serviço é o nosso *auditor* e *analista de desempenho*!
    *   Ele *escuta* todas as mensagens do Kafka.
    *   Verifica se os dados estão *consistentes* em todos os bancos após uma ação.
    *   Registra *tudo* em logs detalhados para análise e depuração.
    *   *Poderia* enviar os logs para o Elasticsearch para análises avançadas de desempenho e uso.


### 2.5. Bancos de Dados🗄️:

#### 2.5.1. PostgreSQL (Relacional) 📦:

*   Ideal para dados *estruturados* e seus *relacionamentos*:
    *   `Jogadores`: Informações dos jogadores.
        *   `username` , `email`, `registration_date`, `platarform` e `region`

#### 2.5.2. MongoDB (Documento) 📋:

*   Bom para dados *flexíveis* ou mais descritivos:
    *   `EstatisticasArmaDetalhada`: Estatísticas de uso (tiros, baixas, etc.), que podem ter campos adicionados.
    *   `Loadout's`: Loadouts possíveis com cada arma.

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

2.  **Clone este Repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO>
    cd cod_project # Ou o nome da sua pasta
    ```

3.  **Execute o Docker Compose (isso vai iniciar todos os sistemas!):**
    ```bash
    docker-compose up -d
    ```

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
## 6. Instalação de Dependências (com Poetry) 弾:

1.  **Instale Poetry:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Instale as Dependências:**

    ```bash
    poetry install
    ```

    (Se preferir usar `pip` e `requirements.txt`, use `pip install -r requirements.txt`)

## 7. Execução do Projeto 🏃‍♂️:

1.  **Verifique se os Contêineres Docker Estão Rodando:**

    ```bash
    docker-compose ps
    ```

    Você deve ver os serviços `postgres`, `mongo`, `cassandra`, `zookeeper` e `kafka` listados como `Up`.

2.  **Crie as Tabelas/Coleções do Banco de Dados:**

    *   **PostgreSQL:** O script para criar as tabelas é executado *automaticamente* quando você inicia a API (graças a um evento `startup`).
    *   **Cassandra:** As tabelas são criadas automaticamente pelo código na primeira vez que a conexão é estabelecida.

3.  **Inicie os Consumidores Kafka (S2 e S3):**

    Abra *dois* terminais separados (e *ative o ambiente virtual* se estiver usando um):

    *   **Terminal 1 (S2):**
        ```bash
        python app/services/message_consumer.py
        ```

    *   **Terminal 2 (S3):**
        ```bash
        python app/services/validation_service.py
        ```

4.  **Inicie a API (FastAPI):**

    Em outro terminal (e *ative o ambiente virtual*):

    ```bash
    uvicorn app.api.main:app --reload
    ```

    O `--reload` é útil durante o desenvolvimento, pois a API reinicia automaticamente sempre que você modifica o código.

## 8. Interação com o Projeto (Simulação) 🎯:

*   **Postman:** Uma ferramenta gráfica para testar APIs.
*   **Insomnia:** Outra ferramenta gráfica, similar ao Postman.
*   **cURL:** Uma ferramenta de linha de comando.
*   **Scripts Python:** Usando a biblioteca `requests`.

**Exemplos de Requisições:**

*   **Registrar Jogador:**
    *   Método: `POST`
    *   Endpoint: `/users/`
    *   Corpo (JSON):

        ```json
        {
          "gamertag": "Soldado123",
          "email": "soldado@example.com",
          "password": "senhaUltraSecreta"
        }
        ```

*   **Criar Loadout:**
    *   Método: `POST`
    *   Endpoint: `/loadouts/` 
    *   Corpo (JSON):

        ```json
        {
          "jogador_id": 1,
          "nome_loadout": "Assalto Furtivo",
          "slot_num": 1,
          "armas": [
            {"arma_id": 5, "slot_tipo": "primaria", "anexos": [10, 15]},
            {"arma_id": 22, "slot_tipo": "secundaria", "anexos": []}
          ]
        }
        ```

*   **Registrar Arma Desbloqueada:**
    *   Método: `POST`
    *   Endpoint: `/weapons/unlock` (você precisará criar este endpoint!)
    *   Corpo (JSON):

        ```json
        {
          "jogador_id": 1,
          "arma_id": 7
        }
        ```

*   **Listar Armas Desbloqueadas por um Jogador:**
    *   Método: `GET`
    *   Endpoint: `/users/{jogador_id}/weapons` (você precisará criar este endpoint!)

## 9. Próximos Passos e Melhorias ⭐

*   **Implementar os Serviços Restantes (S1):** Terminar a lógica dos serviços.
*   **Implementar a Lógica de Validação do S3:** Adicionar a lógica de validação ao `validation_service.py`.
*   **Tratamento de Erros Robusto:** Adicionar tratamento de erros em *todos* os componentes.
*   **Testes:** Escrever testes *unitários* e de *integração*.
*   **Autenticação e Autorização:** Adicionar segurança à API (JWT, OAuth 2.0, etc.). *Nunca* armazene senhas em texto plano!
*   **Simulação Mais Realista:** Criar scripts de simulação que imitem melhor o comportamento dos jogadores.
*   **Adicionar Outras Funcionalidades:** Que tal um sistema de *Perks*? Ou estatísticas de partidas (simuladas)?
*   **Escalabilidade (Avançado):** Investigar técnicas para lidar com muitos jogadores e requisições.
