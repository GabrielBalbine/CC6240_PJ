#!/bin/bash
echo "Aguardando Kafka ficar disponível em kafka:9092..."

while ! python -c "
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    sock.connect(('kafka', 9092))
    sock.close()
    exit(0)  # Sucesso
except Exception as e:
    exit(1)  # Falha
" &> /dev/null; do
  sleep 1
done

echo "Kafka está pronto! Iniciando o producer..."
python ./producer.py