FROM python:3.12-slim
WORKDIR /app
COPY HU_AUTO_UTM_RH_ATGC_SAFE_2K_oneline.sh server.py ./
RUN chmod +x HU_AUTO_UTM_RH_ATGC_SAFE_2K_oneline.sh && test "$(wc -c < HU_AUTO_UTM_RH_ATGC_SAFE_2K_oneline.sh)" -le 2048 && python3 -m py_compile server.py
CMD ["python3","server.py"]
