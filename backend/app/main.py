from fastapi import FastAPI, UploadFile, File
from time import time

from app.core.csv_loader import load_transactions
from app.core.graph_builder import build_graph
from app.core.feature_engine import compute_node_features
from app.core.network_intelligence import (
    compute_network_intelligence,
    compute_behavioral_entropy
)

from app.patterns.cycle_detector import CycleDetector
from app.patterns.smurfing_detector import SmurfingDetector
from app.patterns.shell_detector import ShellDetector

from app.scoring.aggregation_engine import AggregationEngine
from app.utils.json_builder import JSONBuilder
from app.utils.logger import get_logger

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os


app = FastAPI()
app.mount("/_next", StaticFiles(directory="frontend/.next"), name="next")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("frontend/.next/server/pages/index.html")


logger = get_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):

    start_time = time()

    transactions = load_transactions(file.file)
    logger.info("CSV loaded")

    graph = build_graph(transactions)
    compute_node_features(graph)
    compute_network_intelligence(graph)
    compute_behavioral_entropy(graph)

    logger.info("Graph intelligence computed")

    cycle = CycleDetector().detect(graph)
    smurf = SmurfingDetector().detect(graph)
    shell = ShellDetector().detect(graph)

    suspicious, rings = AggregationEngine().aggregate(
        graph, cycle, smurf, shell
    )

    output = JSONBuilder().build(
        suspicious,
        rings,
        graph.number_of_nodes(),
        start_time
    )

    logger.info("Analysis complete")

    return output
