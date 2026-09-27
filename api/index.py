import sys
from pathlib import Path

# Add root folder to sys.path so it imports dashboard and agent_core
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard import ContentAgentHandler

# Expose handler for Vercel Python serverless runtime
app = ContentAgentHandler
handler = ContentAgentHandler
