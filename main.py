import logging
import os

import uvicorn
from dotenv import load_dotenv

from src import app

load_dotenv()
logging.basicConfig(level=logging.INFO)

try:
    import uvloop

    uvloop.install()
except ImportError:
    logging.warning("uvloop is not installed, using default event loop.")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8080))


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
