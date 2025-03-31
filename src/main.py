import os

import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(override=True)
    uvicorn.run(
        app=os.environ.get("ASGI_APP", "infrastructure.api:app"),
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
    )
