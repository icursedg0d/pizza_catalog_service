from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app.routers import category, products, cart
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://pizza-auth-service.onrender.com",
    "https://pizza-catalog-service.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
