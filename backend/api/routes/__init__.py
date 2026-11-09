from fastapi import APIRouter, Depends

from backend.api.dependencies import get_current_user
from backend.api.routes import analysis, auth, compare, documents, tools, upload

auth_router = auth.router
public_router = APIRouter()
public_router.include_router(tools.router, tags=["tools"])
api_router = APIRouter(dependencies=[Depends(get_current_user)])
api_router.include_router(upload.router, tags=["documents"])
api_router.include_router(analysis.router, tags=["documents"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(compare.router, tags=["documents"])
