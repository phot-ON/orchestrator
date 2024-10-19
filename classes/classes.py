from pydantic import BaseModel


class Friend(BaseModel):
    username: str

class Invite(BaseModel):
    username: str
    SessionID: str

class Create(BaseModel):
    pass

class Fetch(BaseModel):
    sessionID: str

class Images(BaseModel):
    images:list
    valid:bool

class Leave(BaseModel):
    sessionID: str

class FCM(BaseModel):
    FCMtoken: str

class Join(BaseModel):
    sessionID: str


class Upload(BaseModel):
    imageID: str
    sessionID: str

class FriendList(BaseModel):
    valid: bool
    users: list

class Session(BaseModel):
    sessionID: str
    valid: bool