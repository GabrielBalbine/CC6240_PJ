from pymongo import MongoClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
def get_mongo_client():
    """Obtém um cliente MongoDB."""
    try:
        client = MongoClient(settings.DATABASE_URL_MONGO)
        return client
    except Exception as e:
        logger.exception("Erro ao conectar com MongoDB:")
        raise

def get_mongo_db():
    """Obtém uma instância do banco de dados MongoDB."""
    client = get_mongo_client()
    db = client["eldenringdb"]  # Mesmo nome do banco PostgreSQL (mas são bancos diferentes)
    return db

# Exemplo de função para inserir uma descrição de chefe
def create_descricao_chefe(chefe_id: int, descricao: str):
    db = get_mongo_db()
    try:
        result = db.descricoeschefes.insert_one({"chefe_id": chefe_id, "texto_completo": descricao})
        return result.inserted_id
    except Exception as e:
        logger.exception(f"Erro ao inserir descrição do chefe {chefe_id} no MongoDB:")
        return None
