import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.app import get_application

app = get_application()

# Redirect the root endpoint "/" to the Swagger UI
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

# Redirect the root endpoint "/hello" to the Swagger UI
@app.get("/hello", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse()

if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True, port=8080)
