from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
from dotenv import load_dotenv

load_dotenv()

def add_cors_middleware(app: FastAPI):
    allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")

    if allowed_origins_str == "*":
        allowed_origins = ["*"]
    else:
        allowed_origins = [o.strip() for o in allowed_origins_str.split(",") if o.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    return app