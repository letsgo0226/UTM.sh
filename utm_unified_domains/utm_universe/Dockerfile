FROM python:3.12-slim
WORKDIR /app
COPY server.py /app/server.py
COPY compute_fabric.py /app/compute_fabric.py
COPY protocols /app/protocols
EXPOSE 8080
CMD ["python3","/app/server.py"]
