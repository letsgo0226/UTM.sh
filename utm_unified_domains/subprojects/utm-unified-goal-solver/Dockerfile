FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN python -c 'import json;r=json.load(open("/app/utm-total-goal-registry.json"));n=sum(map(len,r["layers"].values()));assert n==r["declared_item_count"]==119,(n,r["declared_item_count"]);assert len(r["layers"]["I_sustainable_development_goals"])==r["sdg"]["goal_count"]==17;assert r["sdg"]["target_count"]==169'
ENV PYTHONUNBUFFERED=1
CMD ["python","app_v2.py"]
