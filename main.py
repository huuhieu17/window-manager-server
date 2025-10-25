from fastapi import FastAPI
from app.routes import ws_route
import uvicorn

app = FastAPI(title="Control Server")

app.include_router(ws_route.router)

@app.get("/")
def root():
    return {"message": "Control Server is running"}

if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
