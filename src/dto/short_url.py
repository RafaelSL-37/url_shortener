from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    longUrl: HttpUrl