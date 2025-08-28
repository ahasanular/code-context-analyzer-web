from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.security.rate_limiter import limiter
from app.api.routes import router
from a2wsgi import ASGIMiddleware

app = FastAPI()
app.state.limiter = limiter

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router, prefix="/api")

@app.get("/")
async def serve_index():
    return FileResponse("static/index.html")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

wsgi_app = ASGIMiddleware(app)
