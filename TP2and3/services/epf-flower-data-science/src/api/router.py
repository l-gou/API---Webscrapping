"""API Router for Fast API."""
from fastapi import APIRouter

from src.api.routes import hello, docs, data, load, process, split, train_model, predict,firestore_parameters

router = APIRouter()

router.include_router(docs.router, tags=["docs"])
router.include_router(hello.router, tags=["Hello"])
router.include_router(data.router, tags=["Data"])
router.include_router(load.router, tags=["Load"])
router.include_router(process.router, tags=["Process"])
router.include_router(split.router, tags=["Split"])
router.include_router(train_model.router, tags=["Train Model"])
router.include_router(predict.router, tags=["Predict"])
router.include_router(firestore_parameters.router, tags=["Firestore Parameters"])


