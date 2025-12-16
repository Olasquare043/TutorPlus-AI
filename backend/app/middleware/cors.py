from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def setup_cors(app: FastAPI):
    """Configure CORS middleware"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "https://5173-01kcbrk2tej9p6ce24d5vynm4g.cloudspaces.litng.ai",

            # added backend public
            "https://8000-01kcbrk2tej9p6ce24d5vynm4g.cloudspaces.litng.ai"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )