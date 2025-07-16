from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid
import os

from backend.router.utils.runner import run_tool_background

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

class RunToolRequest(BaseModel):
    tool: str
    inputs: dict

@router.post("/run-tool")
def run_tool_endpoint(req: RunToolRequest, background_tasks: BackgroundTasks):
    tool = req.tool
    inputs = req.inputs
    
    # Generate a unique run_id
    run_id = str(uuid.uuid4())

    # Create output directory for the tool and run
    output_dir = OUTPUTS_DIR / tool / run_id
    os.makedirs(output_dir, exist_ok=True)

    # Log file path
    log_path = output_dir / "log.txt"

    # Construct script path
    script_path = BASE_DIR / "scrapers" / f"{tool}.py"
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="Tool script not found")

    # Add to background task
    background_tasks.add_task(
        run_tool_background,
        tool=tool,
        script_path=str(script_path),
        inputs=inputs,
        log_path=str(log_path)
    )

    return {"run_id": run_id}
