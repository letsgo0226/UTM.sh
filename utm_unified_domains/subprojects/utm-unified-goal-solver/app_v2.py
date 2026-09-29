#!/usr/bin/env python3
"""UTM Unified Goal Solver v2: canonical total-registry overlay."""
import importlib.util, json, os
from pathlib import Path

HERE=Path(__file__).resolve().parent
REG=json.loads((HERE/"utm-total-goal-registry.json").read_text(encoding="utf-8"))
spec=importlib.util.spec_from_file_location("utm_goal_core",HERE/"app.py")
core=importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
core.PROTOCOL="UTM-Unified-Goal-Solver/2.0"
core.GOALS=REG["layers"]
core.GOAL_REGISTRY=REG
core.CACHE=None

if __name__=="__main__":
    port=int(os.environ.get("PORT","8080"))
    print(json.dumps({"protocol":core.PROTOCOL,"world_id":core.WORLD_ID,"kernel":REG["kernel"],"declared_item_count":REG["declared_item_count"],"sdg_goal_count":REG["sdg"]["goal_count"],"potentially_unbounded":REG["semantics"]["potentially_unbounded"],"actual_infinite_physical_compute":REG["semantics"]["actual_infinite_physical_compute"]},ensure_ascii=False),flush=True)
    core.ThreadingHTTPServer(("0.0.0.0",port),core.H).serve_forever()
