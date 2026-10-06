FROM python:3.12-slim
WORKDIR /app
COPY RCD_METACONT_2K_oneline.sh server.py ./
RUN chmod +x RCD_METACONT_2K_oneline.sh
CMD ["python3","server.py"]
