FROM python:3.12-slim
WORKDIR /app
COPY HU_AUTO_UTM_Intrinsic_Godel_Dirichlet_2K_oneline.sh server.py ./
RUN chmod +x HU_AUTO_UTM_Intrinsic_Godel_Dirichlet_2K_oneline.sh && test "$(wc -c < HU_AUTO_UTM_Intrinsic_Godel_Dirichlet_2K_oneline.sh)" -le 2048 && python3 -m py_compile server.py
CMD ["python3","server.py"]
