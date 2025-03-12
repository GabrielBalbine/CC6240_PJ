import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_postgres_connection():
    """Obtém uma conexão com o banco de dados PostgreSQL."""
    try:
        conn = psycopg2.connect(settings.DATABASE_URL_POSTGRES, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Erro ao conectar com PostgreSQL: {e}")
        raise  # Re-lança a exceção para que ela seja tratada em um nível superior

def create_tables():
    """Cria as tabelas no banco de dados PostgreSQL."""
    conn = None  # Inicializa a variável conn
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        with open("app/schemas/elden_ring.sql", "r") as file:
            cursor.execute(file.read())
        conn.commit()
        logger.info("Tabelas PostgreSQL criadas com sucesso!")
    except Exception as e:
        logger.exception("Erro ao criar tabelas PostgreSQL:")
        if conn:
            conn.rollback()
        raise  # Re-lança a exceção
    finally:
        if conn:
            cursor.close()
            conn.close()

# Funções de CRUD (Create, Read, Update, Delete) - Exemplos:
def create_user(user: UserCreate, hashed_password:str):
    conn = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, email, password) VALUES (%s, %s, %s) RETURNING id, username, email",
            (user.username, user.email, hashed_password)
        )
        new_user = cursor.fetchone()
        conn.commit()
        return new_user
    except psycopg2.errors.UniqueViolation:
         raise ValueError("Usuário com esse nome ou email já existe")
    except Exception as e:
        logger.exception("Erro ao criar usuário no PostgreSQL:")
        if conn:
            conn.rollback()  # Desfaz a transação se houver erro
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_user_by_username(username: str):
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário por username ({username}):")
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()

def create_character(user_id: int, character: CharacterCreate):
    conn = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO personagens (usuario_id, nome, classe, nivel) VALUES (%s, %s, %s, %s) RETURNING id, usuario_id, nome, classe",
            (user_id, character.nome, character.classe, 1) # Começa no nível 1
        )
        new_character = cursor.fetchone()
        conn.commit()
        return new_character
    except Exception as e:
        logger.exception("Erro ao criar personagem no PostgreSQL:")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            cursor.close()
            conn.close()
