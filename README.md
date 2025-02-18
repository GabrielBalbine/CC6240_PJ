# ⛏️ Fortnite: Projeto de Persistência Poliglota e Mensageria 🦙

Boas-vindas ao projeto **Fortnite Simplified**! Prepare-se para construir, saquear e... *programar*! 🚀

Este é um projeto *educacional* que explora conceitos de desenvolvimento de software usando elementos do famoso jogo Fortnite como inspiração. Mas atenção: **não vamos implementar a jogabilidade Battle Royale aqui!** 🚫 Nosso foco é o *backend*, usando tecnologias modernas para criar um sistema simplificado que lida com:

*   🛍️ Loja de Itens (Skins, Picaretas, Emotes e mais!)
*   🎒 Inventário do Jogador
*   🏆 Passe de Batalha (versão simplificada)
*   📅 Desafios Diários e Semanais

## 1. Tecnologias Utilizadas: Uma Mochila Cheia de Ferramentas! 🛠️

*   **Linguagem Principal:** Python 🐍 (versátil como um bom construtor!)
*   **Bancos de Dados (nosso "loot"):**
    *   PostgreSQL (Relacional): Para dados que precisam de estrutura e relacionamentos fortes.
    *   MongoDB (Documento): Para dados mais flexíveis, como a rotação da loja diária!
    *   Cassandra (Wide-Column): Para aqueles dados que precisam de acesso rápido e escalabilidade, como estatísticas de itens!
*   **Mensageria (o "ônibus de batalha" dos dados):** Kafka 🚌
*   **API (a "plataforma de lançamento" para interagir com o sistema):** FastAPI 🚀
*   **Gerenciamento de Dependências:** Poetry (ou pip, se preferir)
*   **Containerização (tudo organizado em "baús"):** Docker e Docker Compose 🐳

*   **Bibliotecas Python (nossas "armas"):**
    *   `psycopg2-binary`: Conexão com PostgreSQL.
    *   `pymongo`: Conexão com MongoDB.
    *   `cassandra-driver`: Conexão com Cassandra.
    *   `confluent-kafka`: Cliente Kafka para Python.
    *   `uvicorn`: Servidor ASGI para executar a API FastAPI.
    *   `pydantic`: Validação de dados e configurações.

## 2. Arquitetura: Construindo Nossa Base! 🧱

Nosso projeto segue o estilo de arquitetura de *microserviços*, o que significa que temos vários serviços independentes trabalhando juntos.  Pense neles como diferentes *locais de interesse* no mapa!

### 2.1. Serviços (S1 - Produtores): Os Construtores 👷‍♀️👷‍♂️

Estes serviços são o coração da nossa lógica.  Eles *produzem* mensagens que são enviadas para o Kafka (nosso sistema de mensageria).

*   `user_service`: O "cartório" do jogo, onde os jogadores se registram.
*   `shop_service`: A loja, onde a mágica (e as compras) acontecem!
*   `inventory_service`: O "depósito" onde os jogadores guardam seus itens.
*   `battlepass_service`: O gerente do Passe de Batalha, distribuindo as recompensas.
*   `challenge_service`: O mestre dos desafios, sempre com novas tarefas.

### 2.2. Serviço Consumidor (S2 - Consumidor/Processador): O Coletor 🎒

*   `message_consumer`: Este serviço fica de olho no Kafka, *consumindo* as mensagens e atualizando os bancos de dados de acordo.  Ele é como um jogador coletando recursos!

### 2.3. Serviço de Validação/Logs (S3 - Consumidor): O Inspetor 🕵️‍♀️

*   (Não implementado neste exemplo simplificado, mas importante no *conceito*!)
*   Este serviço seria como um *auditor*, verificando se tudo está em ordem.
*   Ele *consome* todas as mensagens do Kafka.
*   Confere se os dados estão consistentes entre os diferentes bancos de dados.
*   Registra tudo em logs detalhados (para análise e *debugging*).
*   Poderia até enviar os dados para o Elasticsearch para buscas e visualizações incríveis!

### 2.4. API (FastAPI): A Interface Amigável 🤝

*   A API é a *porta de entrada* para interagir com o nosso sistema.
*   Ela oferece *endpoints* (URLs) que você pode acessar para realizar ações (criar usuário, comprar item, etc.).
*   Usa o FastAPI, um framework Python moderno e *rápido*!
*   E, claro, usa modelos Pydantic para garantir que os dados estejam sempre corretos.

### 2.5. Bancos de Dados: Onde Guardamos o Loot! 💰

#### 2.5.1. PostgreSQL (Relacional): O Cofre Seguro 🏦

*   Aqui guardamos os dados que precisam de *estrutura* e *relacionamentos* fortes, como:
    *   `Usuarios`: Informações dos jogadores.
    *   `Itens`: Detalhes dos itens da loja.
    *   `Inventario`: O que cada jogador possui.
    *   `PasseBatalha`: Informações sobre os Passes de Batalha.
    *   `NiveisPasseBatalha`: As recompensas de cada nível.
    *   `ProgressoPasseBatalha`: O progresso de cada jogador.
    *   `Desafios`: Os desafios diários e semanais.
    *   `ProgressoDesafio`: O progresso de cada jogador nos desafios.

#### 2.5.2. MongoDB (Documento): A Mochila Flexível 🎒

*   Ideal para dados que podem mudar com o tempo, ou que não se encaixam perfeitamente em tabelas:
    *   `LojaDiaria`: Os itens em destaque na loja (que mudam todo dia!).
    *   `Eventos`: Informações sobre eventos especiais.
    *   `Noticias`: Novidades e atualizações do jogo.

#### 2.5.3. Cassandra (Wide-Column): O Armazém de Alta Performance 🏭

*   Perfeito para dados que precisam ser acessados *rapidamente* e que podem crescer *muito*:
    *   `EstatisticasItens`: Quantas vezes cada item foi comprado, etc.
    *   `EventosDeJogo`: Um registro de tudo que acontece (login, logout, compra, etc.).
    *   `RankingPasseBatalha`: A classificação dos jogadores no Passe de Batalha.

### 2.6. Mensageria (Kafka): O Ônibus de Batalha dos Dados! 🚌

*   Usamos o Kafka para comunicação *assíncrona* entre os serviços.  Isso significa que os serviços não precisam esperar uns pelos outros para realizar suas tarefas.
*   **Tópicos:**  Como diferentes *rotas* que os dados podem seguir:
    *   `compra_item`
    *   `desafio_completo`
    *   `nivel_passe_batalha`
    *    `login`
    *   `logout`

## 3. Justificativa da Escolha dos Bancos de Dados: Escolhendo as Ferramentas Certas! 🤔

*   **PostgreSQL:** Precisamos de *confiança* e *integridade* para os dados principais (jogadores, itens, inventário). O PostgreSQL, com sua natureza transacional, é como um cofre forte para esses dados.

*   **MongoDB:** Para dados que mudam com frequência (loja diária, eventos), precisamos de *flexibilidade*. O MongoDB, com sua estrutura de documentos, é como uma mochila que se adapta a diferentes cargas.

*   **Cassandra:** Quando o assunto é *velocidade* e *escala*, o Cassandra entra em ação. Ele é perfeito para dados que crescem rapidamente e precisam ser acessados com frequência (estatísticas, logs).

## 4. Configuração do Ambiente: Preparando o Terreno! 🗺️

Usaremos Docker e Docker Compose para criar um ambiente de desenvolvimento *consistente* e *fácil de configurar*.  É como ter um *kit de construção* pronto para usar!

1.  **Instale Docker e Docker Compose:**
    *   Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

2.  **Clone o Repositório (se você tiver acesso a ele):**

    ```bash
    git clone <URL_do_repositorio>
    cd <nome_da_pasta_do_repositorio>
    ```

3.  **Execute o Docker Compose (isso vai construir e iniciar tudo!):**

    ```bash
    docker-compose up -d
    ```

## 5. Estrutura do Projeto: Organizando o Inventário! 🗂️

```markdown
fortnite_project/
├── app/
│   ├── api/                 # Código da API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py          # Ponto de entrada
│   │   ├── routers/         # Rotas (endpoints)
│   │   │   ├── __init__.py
│   │   │   ├── users.py     # Rotas para usuários
│   │   │   ├── shop.py      # Rotas para a loja
│   │   │   └── ...
│   │   └── models.py        # Modelos Pydantic
│   ├── db/                  # Interação com bancos de dados
│   │   ├── __init__.py
│   │   ├── postgres.py      # Funções para PostgreSQL
│   │   ├── mongo.py         # Funções para MongoDB
│   │   └── cassandra.py     # Funções para Cassandra
│   ├── services/            # Lógica de negócio (S1, S2, S3)
│   │   ├── __init__.py
│   │   ├── user_service.py  # Serviço para usuários (S1)
│   │   ├── shop_service.py  # Serviço para a loja (S1)
│   │   ├── message_consumer.py # Serviço consumidor (S2)
│   │   └── ...
│   ├── core/                # Configurações e utilitários
│   │   ├── __init__.py
│   │   ├── config.py        # Configurações
│   │   └── kafka_producer.py # Produtor Kafka genérico
│   └── schemas/             # Schemas SQL
│       ├── __init__.py
│       ├── fortnite.sql
│       └── ...
├── docker-compose.yml       # Arquivo Docker Compose
├── pyproject.toml           # Configuração do Poetry (ou requirements.txt)
└── README.md                # Este arquivo
```

## 6. Instalação de Dependências (com Poetry): Equipando-se para a Batalha! 🛡️

1.  **Instale Poetry:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Instale as Dependências:**

    ```bash
    poetry install
    ```

    (Se você preferir usar `pip` e `requirements.txt`, use `pip install -r requirements.txt`)

## 7. Execução do Projeto: Entrando no Ônibus de Batalha! 🚌

1.  **Verifique se os Contêineres Docker Estão Rodando:**

    ```bash
    docker-compose ps
    ```

    Você deve ver os serviços `postgres`, `mongo`, `cassandra`, `zookeeper` e `kafka` listados como `Up`.

2.  **Crie as Tabelas/Coleções do Banco de Dados:**

    *   **PostgreSQL:** O script para criar as tabelas é executado *automaticamente* quando você inicia a API (graças a um evento `startup`).

3.  **Inicie o Consumidor Kafka (S2):**

    Abra um terminal separado (e *ative o ambiente virtual* se você estiver usando um):

    ```bash
    python app/services/message_consumer.py
    ```

4.  **Inicie a API (FastAPI):**

    Em outro terminal (e *ative o ambiente virtual*):

    ```bash
    uvicorn app.api.main:app --reload
    ```

    O `--reload` é útil durante o desenvolvimento, pois a API reinicia automaticamente sempre que você modifica o código.

## 8. Interação com o Projeto (Simulação): A Hora do Show! 🎮

Como este projeto *não tem a jogabilidade* de Fortnite, você precisará simular as ações dos jogadores. Faça isso enviando requisições HTTP para a API. Você pode usar ferramentas como:

*   **Postman:** Uma ferramenta gráfica para testar APIs.
*   **Insomnia:** Outra ferramenta gráfica, similar ao Postman.
*   **cURL:** Uma ferramenta de linha de comando.
*   **Scripts Python:** Usando a biblioteca `requests`.

**Exemplos de Requisições:**

*   **Criar Usuário:**
    *   Método: `POST`
    *   Endpoint: `/users/`
    *   Corpo (JSON):

        ```json
        {
          "username": "jogador123",
          "email": "jogador@example.com",
          "password": "senhaSegura"
        }
        ```

*   **Comprar Item:**
    *   Método: `POST`
    *   Endpoint: `/shop/buy` (você precisará criar este endpoint!)
    *   Corpo (JSON):

        ```json
        {
          "user_id": 1,
          "item_id": 25
        }
        ```

*   **Listar Inventário:**
    *   Método: `GET`
    *   Endpoint: `/inventory/{user_id}` (você precisará criar este endpoint!)

Você precisará criar *scripts* (em Python ou outra linguagem) para automatizar essas requisições e simular diferentes cenários (muitos jogadores comprando itens ao mesmo tempo, completando desafios, etc.).

## 9. Próximos Passos e Melhorias: Evoluindo o Projeto! 📈

*   **Implementar os Serviços Restantes (S1):** Terminar a lógica dos serviços que ainda não foram completamente implementados.
*   **Implementar o Serviço de Validação/Logs (S3):** Criar o serviço que monitora tudo e garante a consistência dos dados.
*   **Tratamento de Erros Robusto:** Adicionar tratamento de erros adequado em *todos* os componentes (não apenas `print("Erro!")`).
*   **Testes, Testes, Testes!:** Escrever testes *unitários* (para funções individuais) e de *integração* (para testar a interação entre os componentes).
*   **Autenticação e Autorização:** Adicionar segurança à API (JWT, OAuth 2.0, etc.). *Nunca* armazene senhas em texto plano!
*   **Simulação Mais Realista:** Criar scripts de simulação que imitem melhor o comportamento dos jogadores.
*   **Adicionar Outras Funcionalidades:** Que tal presentes entre jogadores? Um sistema de amigos?
*   **Escalabilidade (Avançado):** Se você quiser levar o projeto *muito* a sério, pode investigar técnicas para lidar com um grande número de usuários e requisições.
