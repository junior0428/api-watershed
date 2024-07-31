# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.basin import router as basin_router
from routes.scraper import router as scraper_router
import uvicorn

app = FastAPI(title="API for Watershed Delineation")

""" # static files
app.mount("/public", StaticFiles(directory="public"), name="public") """

# Incluir el router de basin en la aplicación principal
app.include_router(basin_router, prefix="/basin", tags=["Basin Operations"])
app.include_router(scraper_router, prefix="/scraper", tags=["Web Scraping"])

if __name__ == "__main__":
    uvicorn.run("main:app", host='127.0.0.1', port=8000, loop='asyncio', reload=True)