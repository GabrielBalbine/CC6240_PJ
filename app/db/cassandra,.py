from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
def get_cassandra_session():
    """Obtém uma sessão do Cassandra."""
    try:
        # Configuração básica (sem autenticação)
        cluster = Cluster([settings.DATABASE_URL_CASSANDRA])
        session = cluster.connect()

        # Cria o keyspace, SE NÃO existir
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS eldenringkeyspace
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
        """)
        session.set_keyspace("eldenringkeyspace") # Usa o keyspace
        return session

    except Exception as e:
        logger.exception("Erro ao conectar com Cassandra:")
        raise

def create_cassandra_tables():
    session = get_cassandra_session()
    try:
        session.execute("""
            CREATE TABLE IF NOT EXISTS eventos_de_jogo (
                timestamp timestamp,
                usuario_id int,
                tipo_evento text,
                detalhes text,
                PRIMARY KEY (timestamp, usuario_id)
            ) WITH CLUSTERING ORDER BY (usuario_id ASC);
        """)

        session.execute("""
            CREATE TABLE IF NOT EXISTS ranking_chefes_derrotados (
                num_chefes_derrotados int,
                usuario_id int,
                PRIMARY KEY (num_chefes_derrotados, usuario_id)
            ) WITH CLUSTERING ORDER BY (usuario_id ASC);
        """)
        logger.info("Tabelas Cassandra criadas com sucesso!")

    except Exception as e:
        logger.exception("Erro ao criar tabelas Cassandra:")
        raise
    finally:
        session.cluster.shutdown() #Fecha o cluster

# Exemplo de função para inserir um evento de jogo
def insert_evento_jogo(timestamp, usuario_id: int, tipo_evento: str, detalhes: str):
    session = get_cassandra_session()
    try:
        session.execute(
            "INSERT INTO eventos_de_jogo (timestamp, usuario_id, tipo_evento, detalhes) VALUES (%s, %s, %s, %s)",
            (timestamp, usuario_id, tipo_evento, detalhes)
        )
    except Exception as e:
        logger.exception(f"Erro ao inserir evento no Cassandra ({tipo_evento}, user_id={usuario_id}):")
        # Não faz rollback, pois o Cassandra não tem transações como o PostgreSQL
