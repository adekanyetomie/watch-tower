from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "welcome"}

@app.get("/healthz")
async def health_check():
    return {"message": "ok"}