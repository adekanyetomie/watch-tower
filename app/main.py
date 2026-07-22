from fastapi import FastAPI

app = FastAPI(
     title="Watchtower",
    description="Uptime monitor for my own estate"
)

@app.get("/")
def read_root():
    return {"service": "watchtower", "status": "ok"}

@app.get("/healthz")
async def health_check():
    return {"message": "ok"}