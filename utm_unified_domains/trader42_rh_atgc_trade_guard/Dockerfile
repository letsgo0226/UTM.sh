FROM python:3.12-slim
WORKDIR /app
COPY core.py server.py test_core.py ./
RUN python3 -m py_compile core.py server.py test_core.py && python3 -m unittest -v test_core.py
CMD ["python3","server.py"]
