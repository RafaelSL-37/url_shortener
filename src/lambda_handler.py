import json
from fastapi import FastAPI
from mangum import Mangum
from app import app as fastapi_app

# Lambda handler wraps FastAPI app
lambda_handler = Mangum(fastapi_app)
