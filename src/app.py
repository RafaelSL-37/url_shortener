import os
import string
from http.client import HTTPException
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.getenv("DATABASE_NAME", "url_shortener")
COLLECTION = "urls"
SHORT_LEN = 6

app = FastAPI()
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]


class ShortenRequest(BaseModel):
    longUrl: HttpUrl


async def gen_unique_short():
    coll = db[COLLECTION]

    while True:
        s = "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))
        if not await coll.find_one({"short": s}):
            return s


@app.post("/api/urls/shorten")
async def shorten(req: ShortenRequest):
    coll = db[COLLECTION]
    short = await gen_unique_short()

    doc = {"short": short, "longUrl": str(req.longUrl), "clicks": 0}
    await coll.insert_one(doc)

    base = os.getenv("BASE_URL", "http://localhost:8000")

    return {"shortUrl": f"{base}/{short}"}


@app.get("/api/urls/{short}")
async def get_mapping(short: str):
    doc = await db[COLLECTION].find_one({"short": short})

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    
    return {"longUrl": doc["longUrl"], "clicks": doc.get("clicks", 0)}


@app.get("/{short}")
async def redirect_short(short: str):
    coll = db[COLLECTION]
    doc = await coll.find_one_and_update({"short": short}, {"$inc": {"clicks": 1}})

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    
    return RedirectResponse(doc["longUrl"])