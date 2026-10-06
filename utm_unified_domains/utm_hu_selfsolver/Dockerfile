FROM python:3.12-slim
WORKDIR /app
COPY UTM_HU_SELFSOLVER_2K_oneline.sh server.py ./
RUN chmod +x UTM_HU_SELFSOLVER_2K_oneline.sh && test "$(wc -c < UTM_HU_SELFSOLVER_2K_oneline.sh)" -le 2048
CMD ["python3","server.py"]
