import os

from dotenv import load_dotenv
import uvicorn
import os

if __name__ == "__main__":
    load_dotenv(override=True)
    uvicorn.run(
        app=os.environ["ASGI_APP"],
        host=os.environ["HOST"],
        port=int(os.environ["PORT"]), 
    )