-- Cria a tabela de usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL  -- Armazenar senhas com hashing!
);

-- Cria a tabela de personagens
CREATE TABLE IF NOT EXISTS personagens (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
    nome VARCHAR(50) NOT NULL,
    classe VARCHAR(50) NOT NULL,
    nivel INTEGER DEFAULT 1
);

-- Cria a tabela de chefes
CREATE TABLE IF NOT EXISTS chefes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    area VARCHAR(255),
    recompensa_item_id INTEGER REFERENCES itens(id) ON DELETE SET NULL
);

-- Cria a tabela de relação entre personagens e chefes derrotados
CREATE TABLE IF NOT EXISTS personagem_chefe (
    personagem_id INTEGER REFERENCES personagens(id) ON DELETE CASCADE,
    chefe_id INTEGER REFERENCES chefes(id) ON DELETE CASCADE,
    derrotado BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (personagem_id, chefe_id)
);

-- Cria a tabela de itens
CREATE TABLE IF NOT EXISTS itens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50)
);

-- Cria a tabela de inventário
CREATE TABLE IF NOT EXISTS inventario (
    personagem_id INTEGER REFERENCES personagens(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES itens(id) ON DELETE CASCADE,
    quantidade INTEGER DEFAULT 1,
    PRIMARY KEY (personagem_id, item_id)
);

-- Cria tabela de atributos
CREATE TABLE IF NOT EXISTS atributos(
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
);
-- Cria tabela de relação entre personagens e atributos.
CREATE TABLE IF NOT EXISTS personagem_atributo(
    personagem_id INTEGER REFERENCES personagens(id) ON DELETE CASCADE,
    atributo_id INTEGER REFERENCES atributos(id) ON DELETE CASCADE,
    valor INTEGER NOT NULL,
    PRIMARY KEY (personagem_id, atributo_id)
);
