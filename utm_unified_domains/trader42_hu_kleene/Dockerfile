FROM python:3.12-slim
WORKDIR /app
COPY TRADER42_HU_KLEENE_2K_oneline.sh server.py ./
RUN chmod +x TRADER42_HU_KLEENE_2K_oneline.sh && test "$(wc -c < TRADER42_HU_KLEENE_2K_oneline.sh)" -le 2048
CMD ["python3","server.py"]
