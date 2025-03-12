# ⚔️ Elden Ring Simplified: Projeto de Persistência Poliglota e Mensageria 🛡️

[![Elden Ring Logo](https://cdn11.bigcommerce.com/s-k0hjo2yyrq/images/stencil/1280x1280/products/1106/4307/Elden_Ring_Standard_Edition_Product_Banner__89855.1726738824.jpg?c=1)](https://www.eldenring.com/)

Saudações, Maculado! Bem-vindo ao projeto **Elden Ring Simplified**! Prepare-se para explorar as Terras Intermédias... *mas sem morrer (muito)!* 😉

## O Que é Este Projeto? 🤔

Este é um projeto *educacional* que usa elementos de Elden Ring para criar um sistema *backend* simplificado.  Imagine que você está construindo um "diário de bordo" para registrar o seu progresso no jogo, mas sem precisar programar a parte da luta em si.  Aqui, você vai:

*   Criar personagens.
*   Registrar quais chefes (bosses) você derrotou.
*   Anotar quais itens você encontrou e equipou.
*   (Opcional) Acompanhar os níveis e atributos do seu personagem.

A ideia principal é aprender como construir sistemas de software usando diferentes tipos de bancos de dados e um sistema de mensagens (como se fosse um "WhatsApp" para os diferentes pedaços do programa se comunicarem). É como aprender a forjar armas e armaduras, mas para *código*!

**Importante:** Este projeto é para *desenvolvedores* (ou aspirantes a desenvolvedores) aprenderem na prática. Ele *não* é um jogo completo, e *não* tem a jogabilidade de Elden Ring.

## 1. Tecnologias Utilizadas: Seu Arsenal de Desenvolvimento! ⚒️

*   **Linguagem Principal:** Python 🐍 (versátil como a Espada Reta!)
*   **Bancos de Dados (onde guardamos nossos tesouros):**
    *   PostgreSQL (Relacional): Para dados que precisam de estrutura e relacionamentos (personagens, chefes, itens...).
    *   MongoDB (Documento): Para dados mais flexíveis, como descrições detalhadas de chefes e itens.
    *   Cassandra (Wide-Column): Para dados que precisam de acesso *super rápido* e podem crescer *muito*, como logs de eventos.
*   **Mensageria (nosso "corcel espectral" para transportar dados):** Kafka 🐎
*   **API (a "graça" que nos permite interagir com o sistema):** FastAPI ✨
*   **Gerenciamento de Dependências:** Poetry (ou pip, se você preferir)
*   **Containerização (tudo organizado em "frascos"):** Docker e Docker Compose 🏺

*   **Bibliotecas Python (nossas "magias"):**
    *   `psycopg2-binary`: Conexão com PostgreSQL.
    *   `pymongo`: Conexão com MongoDB.
    *   `cassandra-driver`: Conexão com Cassandra.
    *   `confluent-kafka`: Cliente Kafka para Python.
    *   `uvicorn`: Servidor ASGI para executar a API FastAPI.
    *   `pydantic`: Validação de dados e configurações.
    *   `logging`: Para gerar logs detalhados.

## 2. Arquitetura: O Mapa das Terras Intermédias (do Código)! 🗺️

Nosso projeto usa uma arquitetura de *microserviços*.  Isso significa que temos vários "pequenos programas" independentes trabalhando juntos. Pense neles como diferentes *áreas* do mapa de Elden Ring!

### 2.1. Serviços (S1 - Produtores): Os NPCs que Fazem as Coisas Acontecerem! 🧙‍♂️

Esses serviços são o *coração* do nosso sistema. Eles realizam as ações principais e *produzem* mensagens que são enviadas para o Kafka.

*   `user_service`: O "guardião" dos usuários, que cuida do registro e autenticação.
*   `character_service`: O "criador de personagens", que permite criar e gerenciar seus personagens.
*   `boss_service`: O "registrador de conquistas", que anota quais chefes você derrotou.
*   `item_service`: O "mestre dos itens", que cuida do inventário e de equipar itens.
*   `attribute_service`: O "distribuidor de atributos", que permite aumentar seus níveis (opcional).

### 2.2. Serviço Consumidor (S2 - Consumidor/Processador): O Mensageiro ✉️

*   `message_consumer`: Este serviço fica de olho no Kafka, *consumindo* as mensagens e atualizando os bancos de dados. Ele é como um mensageiro que entrega as notícias por todo o reino!

### 2.3. Serviço de Validação/Logs (S3 - Consumidor): O Escriba Real 📜

*   `validation_service`: Este serviço é o nosso *historiador* e *inspetor de qualidade*!
    *   Ele *ouve* atentamente todas as mensagens do Kafka.
    *   Verifica se os dados em todos os bancos de dados estão *corretos* e *consistentes*.
    *   Registra *tudo* em logs detalhados (para podermos investigar qualquer problema!).
    *   *Poderia* (em um projeto mais avançado) enviar os logs para o Elasticsearch para buscas e análises super detalhadas.

### 2.4. API (FastAPI): A Grande Biblioteca de Raya Lucaria 📚

*   A API é a nossa *porta de entrada* para o sistema. É como a Grande Biblioteca, onde você pode encontrar informações e realizar ações.
*   Ela oferece *endpoints* (URLs) que você acessa para fazer coisas como criar um personagem, registrar um chefe derrotado, etc.
*   Usa o FastAPI, um framework Python moderno e *rápido*!
*   E, claro, usa modelos Pydantic para garantir que os dados estejam sempre corretos.

### 2.5. Bancos de Dados: Onde Guardamos Nossos Tesouros! 💎

#### 2.5.1. PostgreSQL (Relacional): O Cofre Real 👑

*   Aqui guardamos os dados que precisam de *estrutura* e *relacionamentos* fortes, como:
    *   `Usuarios`: Informações dos jogadores.
    *   `Personagens`: Detalhes dos seus personagens.
    *   `Chefes`: Informações sobre os chefes do jogo.
    *   `PersonagemChefe`: Quais chefes cada personagem derrotou.
    *   `Itens`: Detalhes dos itens.
    *   `Inventario`: Quais itens cada personagem possui.
    *   `Atributos`: Os atributos do jogo (Força, Destreza, etc.)
    *  `PersonagemAtributo`: Atributos do personagem.

#### 2.5.2. MongoDB (Documento): A Biblioteca Flexível 📖

*   Ideal para dados que podem ter informações adicionais ou que não se encaixam perfeitamente em tabelas:
    *   `DescricoesChefes`: Descrições detalhadas dos chefes (com história, dicas, etc.).
    *   `LoreItens` : Descrições mais aprofundadas sobre a história do item.

#### 2.5.3. Cassandra (Wide-Column): O Arquivo de Alta Performance ⚡

*   Perfeito para dados que precisam ser acessados *muito rapidamente* e que podem crescer *muito*:
    *   `EventosDeJogo`: Um registro de tudo o que acontece (chefe derrotado, item encontrado, etc.).
    *   `RankingChefesDerrotados`: Uma tabela para mostrar quantos chefes cada jogador derrotou.

### 2.6. Mensageria (Kafka): O Corcel Espectral dos Dados! 🐎

*   Usamos o Kafka para comunicação *assíncrona* entre os serviços. É como se os serviços enviassem mensagens uns aos outros em vez de falar diretamente.
*   **Tópicos:**  Como diferentes *caminhos* que as mensagens podem seguir:
    *   `chefe_derrotado`
    *   `item_encontrado`
    *   `item_equipado`
    *   `personagem_criado`
    *   `login`
    *   `logout`

## 3. Justificativa da Escolha dos Bancos de Dados: Cada Tesouro em Seu Lugar! 🗺️

*   **PostgreSQL:** Precisamos de *confiança* e *integridade* para os dados principais (jogadores, personagens, chefes, itens). O PostgreSQL é como um cofre forte para esses dados.

*   **MongoDB:** Para dados que precisam de mais *flexibilidade* (descrições detalhadas), o MongoDB é perfeito. Ele é como uma biblioteca onde cada livro pode ter um formato diferente.

*   **Cassandra:** Quando o assunto é *velocidade* e *escala*, o Cassandra é imbatível. Ele é ideal para registrar eventos e gerar rankings.

## 4. Configuração do Ambiente: Preparando Sua Jornada! 🧭

Vamos usar Docker e Docker Compose para criar um ambiente de desenvolvimento *consistente* e *fácil de configurar*. É como ter um mapa do tesouro que te leva direto ao código!

1.  **Instale Docker e Docker Compose:**
    *   Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)
    *   Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

2.  **Clone o Repositório (se você tiver acesso a ele):**
    ```bash
    git clone <URL_do_repositorio>
    cd <nome_da_pasta_do_repositorio>
    ```

3.  **Execute o Docker Compose (isso vai preparar tudo!):**
    ```bash
    docker-compose up -d
    ```

## 5. Estrutura do Projeto: O Inventário do Código! 🎒

```markdown
elden_ring_project/
├── app/
│   ├── api/                 # Código da API (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py          # Ponto de entrada
│   │   ├── routers/         # Rotas (endpoints)
│   │   │   ├── __init__.py
│   │   │   ├── users.py     # Rotas para usuários
│   │   │   ├── characters.py   # Rotas para personagens
│   │   │   └── ...          # Outras rotas
│   │   └── models.py        # Modelos Pydantic
│   ├── db/                  # Interação com bancos de dados
│   │   ├── __init__.py
│   │   ├── postgres.py      # Funções para PostgreSQL
│   │   ├── mongo.py         # Funções para MongoDB
│   │   └── cassandra.py     # Funções para Cassandra
│   ├── services/            # Lógica de negócio (S1, S2, S3)
│   │   ├── __init__.py
│   │   ├── user_service.py      # Serviço de usuários (S1)
│   │   ├── character_service.py # Serviço de personagens (S1)
│   │   ├── boss_service.py      # Serviço de chefes (S1)
│   │   ├── item_service.py      # Serviço de itens (S1)
│   │   ├── message_consumer.py  # Serviço consumidor (S2)
│   │   └── validation_service.py # Serviço de validação/logs (S3)
│   ├── core/                # Configurações e utilitários
│   │   ├── __init__.py
│   │   ├── config.py        # Configurações
│   │   └── kafka_producer.py # Produtor Kafka genérico
│   └── schemas/             # Schemas SQL
│       ├── __init__.py
│       ├── elden_ring.sql     # Schema do PostgreSQL
│       └── ...
├── docker-compose.yml       # Arquivo Docker Compose
├── pyproject.toml           # Configuração do Poetry (ou requirements.txt)
└── README.md                # Este arquivo
```

## 6. Instalação de Dependências (com Poetry): Fortalecendo Suas Armas! 💪

1.  **Instale Poetry:**

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2.  **Instale as Dependências:**

    ```bash
    poetry install
    ```

    (Se preferir usar `pip` e `requirements.txt`, use `pip install -r requirements.txt`)

## 7. Execução do Projeto: Rumo à Grande Árvore Térrea! 🌳

1.  **Verifique se os Contêineres Docker Estão Rodando:**

    ```bash
    docker-compose ps
    ```

    Você deve ver os serviços `postgres`, `mongo`, `cassandra`, `zookeeper` e `kafka` listados como `Up`.

2.  **Crie as Tabelas/Coleções do Banco de Dados:**

    *   **PostgreSQL:** O script para criar as tabelas é executado *automaticamente* quando você inicia a API (graças a um evento `startup`).

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

## 8. Interação com o Projeto (Simulação): Testando Suas Habilidades! ⚔️

Como este projeto *não tem a jogabilidade* de Elden Ring, você precisará simular as ações dos jogadores. Faça isso enviando requisições HTTP para a API. Você pode usar ferramentas como:

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
          "username": "maculado123",
          "email": "maculado@example.com",
          "password": "senhaForte"
        }
        ```

*   **Criar Personagem:**
    *   Método: `POST`
    *   Endpoint: `/characters/` (você precisará criar este endpoint!)
    *   Corpo (JSON):

        ```json
        {
          "user_id": 1,
          "nome": "Cavaleiro da Noite",
          "classe": "Cavaleiro"
        }
        ```

* **Registrar Chefe Derrotado:**
    *   Método: `POST`
    *   Endpoint: `/bosses/defeat`
    *   Corpo (JSON):

        ```json
        {
          "personagem_id": 1,
          "chefe_id": 3
        }
        ```

*   **Listar Chefes Derrotados por um Personagem:**
    *   Método: `GET`
    *   Endpoint: `/characters/{personagem_id}/bosses` (você precisará criar este endpoint!)

Você precisará criar *scripts* (em Python ou outra linguagem) para automatizar essas requisições e simular diferentes cenários.

## 9. Próximos Passos e Melhorias: Rumo à Perfeição! 🏆

*   **Implementar os Serviços Restantes (S1):** Terminar a lógica dos serviços.
*   **Implementar a Lógica de Validação do S3:** Adicionar a lógica de validação ao `validation_service.py`.
*   **Tratamento de Erros Robusto:** Adicionar tratamento de erros em *todos* os componentes.
*   **Testes, Testes, Testes!:** Escrever testes *unitários* e de *integração*.
*   **Autenticação e Autorização:** Adicionar segurança à API (JWT, OAuth 2.0, etc.). *Nunca* armazene senhas em texto plano!
*   **Simulação Mais Realista:** Criar scripts de simulação que imitem melhor o comportamento dos jogadores.
*   **Adicionar Outras Funcionalidades:** Que tal um sistema de níveis para os personagens? Ou um mapa (mesmo que em texto)?
*   **Escalabilidade (Avançado):** Se você quiser se aprofundar, pode investigar técnicas para lidar com muitos usuários e requisições.

Que a graça te guie, Maculado! E divirta-se construindo este projeto! ✨
