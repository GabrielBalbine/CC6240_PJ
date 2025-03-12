from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL_POSTGRES: str = "postgresql://eldenringuser:eldenringpassword@localhost:5432/eldenringdb"
    DATABASE_URL_MONGO: str = "mongodb://localhost:27017/"
    DATABASE_URL_CASSANDRA: str = "localhost"  # Cassandra usa apenas o host
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

settings = Settings()
