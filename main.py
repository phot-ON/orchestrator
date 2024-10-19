from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from requests import session

from classes.classes import *
from classes.services import *
from fastapi.staticfiles import StaticFiles
import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from pydantic import BaseModel
from fastapi import HTTPException, FastAPI, Response, Depends, Header
from fastapi import Cookie
from typing import Annotated
import firebase_admin
from firebase_admin import messaging

const = constants()
app = FastAPI()
appNotif = firebase_admin.initialize_app()
app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")
templates = Jinja2Templates(directory="/code/app/templates")


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(name="home.html", request=request)


@app.get("/login/github")
async def gitlogin(request: Request, response: Response):
    state = newState()

    response.set_cookie(key="stateKey", value=state)
    response.headers["Content-Type"] = "text/html"

    url=f'https://github.com/login/oauth/authorize?client_id=Ov23liuzcWWDAiy7CPMV&scope=user,user:email&redirect_uri={const.BASE_URL_MY}/auth/login/github&state={state}'

    return f"<html><script>window.location = '{url}' </script></html>"
@app.get("/login/discord")
async def gitdiscord(request: Request, response: Response):
    state = newState()

    response.set_cookie(key="stateKey", value=state)
    response.headers["Content-Type"] = "text/html"

    url=f'https://discord.com/oauth2/authorize?client_id=1296907048360874004&response_type=code&redirect_uri={const.BASE_URL_MY}/auth/login/discord&scope=identify+email&state={state}'

    return f"<html><script>window.location = '{url}' </script></html>"

@app.get("/auth/login/github")
async def authGithub(code:str, state:str, response: Response, stateKey: Annotated[str | None, Cookie()] = None):
    response.set_cookie(key="stateKey", value="NONE")
    if state == stateKey:
        resp = requests.get(f"{const.BASE_URL_GAR}/auth/login/github", params={"Code":code})
        if resp.status_code == 200:
            addUser(resp.json()["user"]["email"])
            return RedirectResponse(url="photon://login/{}".format(resp.json()["token"]))
        else:
            return resp.text
    return "CAN NOT ALLOW"

@app.get("/auth/login/discord")
async def authDiscord(code:str, state:str, response: Response, stateKey: Annotated[str | None, Cookie()] = None):
    response.set_cookie(key="stateKey", value="NONE")
    if state == stateKey:
        resp = requests.get(f"{const.BASE_URL_GAR}/auth/login/discord", params={"Code":code})
        if resp.status_code == 200:
            addUser(resp.json()["user"]["email"])
            return RedirectResponse(url="photon://login/{}".format(resp.json()["token"]))
        else:
            return resp.text
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "CAN NOT ALLOW"

@app.get("/auth/validate")
async def validate(token: str, response: Response) -> str:
    validity = valid(token)
    try:
        if validity[0]:
            addUser(validity[1]["email"])
            response.status_code = status.HTTP_200_OK
            return "VALID"
    except:
        pass
    response.status_code = status.HTTP_401_UNAUTHORIZED

    return "INVALID"

@app.get("/auth/session")
async def validateSession(sessionID:str, Authorization:str, request: Request, response: Response) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        users = getSessionUsers(sessionID)
        if user in users:
            return "VALID"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID"
@app.get("/401")
async def error(request: Request, response: Response):
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "TOKEN ERROR"

@app.post("/friend")
async def friend(body:Friend, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user1 = validity[1]["email"]
        user2 = body.username
        makeFriend(user1, user2)
        return "SUCCESS"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID REQUEST"

@app.get("/friend")
async def friend(request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> FriendList:
    validity = valid(Authorization)
    if validity[0]:
        try:
            return getFriends(validity[1]["email"])
        except:
            return FriendList(users=[], valid=False)

    response.status_code = status.HTTP_401_UNAUTHORIZED
    return FriendList(users=[], valid=False)

@app.post("/FCM")
async def FCMtoken(body:FCM, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        if setFCM(user, body.FCMtoken):
            return "SUCCESS"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID REQUEST"

@app.post("/create")
async def create(body:Create, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> Session:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        sessID = createSession(user)
        if sessID != "":
            return Session(sessionID=sessID, valid=True)
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Session(valid=False, sessionID="")

@app.post("/join")
async def join(body:Join, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> Session:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        sessID = joinSession(user, body.sessionID)
        if sessID != "false":
            return Session(sessionID=sessID, valid=True)
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Session(sessionID="", valid=False)

@app.post("/upload")
async def upload(body:Upload, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        users = getSessionUsers(body.sessionID)
        if uploadImage(body.imageID, body.sessionID):
            notifyImage(user, users, body.imageID)
            return "SUCCESS"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID REQUEST"

@app.post("/leave")
async def leave(body:Leave, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        if leaveSession(user, body.sessionID):
            return "SUCCESS"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID REQUEST"

@app.post("/fetch")
async def fetch(body:Fetch, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> Images:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        images = getSessionImages(body.sessionID)
        if len(images) > 0:
            return Images(images=images, valid=True)
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return Images(images=[], valid=False)

@app.post("/invite")
async def invite(body:Invite, request: Request, response: Response, Authorization: Annotated[str | None, Header()] = None) -> str:
    validity = valid(Authorization)
    if validity[0]:
        user = validity[1]["email"]
        if inviteFriend(user, body.username, body.SessionID):
            return "SUCCESS"
    response.status_code = status.HTTP_401_UNAUTHORIZED
    return "INVALID REQUEST"

@app.get("/invite")
async def invite(sessionID:str, request: Request, response: Response) -> RedirectResponse:
    return RedirectResponse(url="photon://joinSession/{}".format(sessionID))
