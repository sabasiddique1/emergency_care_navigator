"""Memory management: session state and long-term memory."""
import os
import json
from typing import Optional
from app.models import MemoryBank
from app.observability import log_event

# Memory file path - use /tmp on Vercel/serverless
if os.getenv("VERCEL"):
    MEM_PATH = "/tmp/memory_bank.json"
else:
    MEM_PATH = "memory_bank.json"


def load_memory() -> MemoryBank:
    """Load memory bank from JSON file."""
    if not os.path.exists(MEM_PATH):
        return MemoryBank()
    try:
        with open(MEM_PATH, "r", encoding="utf-8") as f:
            return MemoryBank(**json.load(f))
    except Exception:
        return MemoryBank()


def save_memory(mem: MemoryBank) -> None:
    """Save memory bank to JSON file."""
    try:
        # Use atomic write: write to temp file first, then rename
        temp_file = f"{MEM_PATH}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(mem.model_dump(), f, indent=2)
        os.replace(temp_file, MEM_PATH)
    except Exception as e:
        log_event("memory_save_error", error=str(e), path=MEM_PATH)
        raise






