from pydantic import BaseModel, HttpUrl


class UrlShortenRequest(BaseModel):
    longUrl: HttpUrl