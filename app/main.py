from typing import Optional, Union
from app.protocol import pingServer
from starlette.responses import Response
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import base64


api = FastAPI()


# Pydantic models for API Documentation
class Version(BaseModel):
    name: str
    protocol: int

class Players(BaseModel):
    max: int
    online: int

class PingResponse(BaseModel):
    version: Version
    players: Players
    motd: Union[str, dict]


def getServerStatus(ip: str, port: int) -> PingResponse:
    rawResponse = pingServer(ip=ip, port=port)
    response = json.loads(rawResponse.get("results"))

    # Getting the version
    rawVersion = response.get("version")
    version = Version(
        name = rawVersion.get("name", ""),
        protocol = rawVersion.get("protocol", -1)
    )

    # Getting the players
    rawPlayers = response.get("players")
    players = Players(
        max = rawPlayers.get("max", -1),
        online = rawPlayers.get("online", -1)
    )

    # Building the ping response
    pingResponse = PingResponse(
        version = version,
        players = players,
        motd = response.get("description", "")
    )

    return pingResponse

def getServerIconBase64(ip: str, port: int) -> str:
    rawResponse = pingServer(ip = ip, port = port)
    response = json.loads(rawResponse.get("results"))
    b64 = response.get("favicon").split(",")[1]
    return b64

def getServerIcon(ip: str, port: int) -> bytes:
    return base64.b64decode(getServerIconBase64(ip, port))


@api.get("/", response_model=PingResponse)
def ping(
    ip: str,
    port: Optional[int] = 25565
) -> PingResponse:
    try:
        response = getServerStatus(ip, port)
        return response
    except Exception as e:
        print(e)
        raise HTTPException(400, "Requested server timed out")

@api.get("/favicon")
def pingFavicon(
    ip: str,
    port: Optional[int] = 25565
) -> bytes:
    try:
        response = Response(content=getServerIcon(ip, port), media_type="image/png");
        return response
    except Exception:
        raise HTTPException(400, "Requested server timed out")
