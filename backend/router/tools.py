# backend/routers/tools.py
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import json
from functools import partial
from pathlib import Path
from backend.router.utils.runner import run_tool_background

router = APIRouter()


BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_FILE = BASE_DIR / "tools.json"
OUTPUT_DIR = BASE_DIR / "outputs"
SCRAPER_DIR = BASE_DIR / "scrapers"

with open(TOOLS_FILE) as f:
    TOOLS = json.load(f)

class RunRequest(BaseModel):
    tool: str
    inputs: dict

@router.get("/scrapers")
def list_tools():
    # return {"tools": TOOLS}
    tools_with_normalized_keys = []
    for tool in TOOLS:
        updated_tool = tool.copy()
        if "states" in updated_tool:
            updated_tool["valid_states"] = updated_tool["states"]
            del updated_tool["states"]

        if "cities" in updated_tool:
            updated_tool["valid_cities"] = updated_tool["cities"]
            del updated_tool["cities"]

        tools_with_normalized_keys.append(updated_tool)

    return {"tools": tools_with_normalized_keys}


@router.post("/run-tool")
def run_tool(req: RunRequest, background_tasks: BackgroundTasks):
    tool = next((t for t in TOOLS if t["name"] == req.tool), None)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    script_path = BASE_DIR / tool["script_path"]
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Script not found")

    run_id = str(uuid4())
    log_file = OUTPUT_DIR / req.tool / run_id / "log.txt"

    background_tasks.add_task(
        partial(run_tool_background, str(script_path), req.inputs, run_id, log_file)
    )
    return {"run_id": run_id}

@router.get("/log/{tool}/{run_id}")
def read_log(tool: str, run_id: str):
    log_path = OUTPUT_DIR / tool / run_id / "log.txt"
    if not log_path.exists():
        return "Waiting for logs..."
    return log_path.read_text()
