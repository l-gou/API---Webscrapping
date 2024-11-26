from fastapi import APIRouter
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

router = APIRouter()

# Redirect the root endpoint "/" to the Swagger UI
@router.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
