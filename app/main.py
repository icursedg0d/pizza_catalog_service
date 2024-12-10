from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.routers import category, products, cart

app = FastAPI()


@app.get("/")
async def welcome() -> dict:
    return {"message": "pizza-catalog"}


app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.include_router(category.router)
app.include_router(products.router)
app.include_router(cart.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8002, reload=True)
