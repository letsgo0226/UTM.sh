FROM python:3.12-slim
WORKDIR /app
COPY app.py axiom_verifier.py /app/
COPY axioms /app/axioms
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8080
CMD ["python3","app.py"]
