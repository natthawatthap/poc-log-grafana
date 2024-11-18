python3 -m venv venv
source venv/bin/activate

docker run -d --name=prometheus -p 9090:9090 \
-v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
prom/prometheus

docker run -d --name=grafana -p 3000:3000 grafana/grafana

uvicorn app:app --host 0.0.0.0 --port 8000


docker run -d --name=loki -p 3100:3100 grafana/loki:latest

http://host.docker.internal:3100

docker-compose up -d

Grafana Dashboard ID (e.g., for Node Exporter: 1860).