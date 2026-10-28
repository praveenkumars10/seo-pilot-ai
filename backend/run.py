import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

import uvicorn
from backend.app.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting SEO Pilot AI Backend on http://127.0.0.1:{settings.PORT}")
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=settings.PORT, reload=True)

