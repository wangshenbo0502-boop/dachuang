"""Test bootstrap for the standalone knowledge package."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_ROOT = ROOT / "knowledge"
if str(KNOWLEDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_ROOT))
