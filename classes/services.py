from firebase_admin import messaging
import requests
import string
import random

from classes.classes import *
from classes.constants import constants

const = constants()

def newState():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(const.stateLength))
    return state

def valid(token):
    resp = requests.get(f"{const.BASE_URL_GAR}/auth/validate", params={"token":token})
    try:
        return [resp.status_code == 200, resp.json()]
    except:
        return [False, None]


def makeFriend(user1:str, user2:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/AddFriend", data={"Username1":user1, "Username2":user2})

def getFriends(user:str):
    resp = requests.get(f"{const.BASE_URL_SAT}/GetFriends?Username={user}")
    return FriendList(users=resp.json(), valid=True)


def setFCM(user:str, fcm:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/SetUserFCM", data={"Username":user, "FCM":fcm}).text
    return resp == "true"

def getFMC(user:str):
    resp = requests.get(f"{const.BASE_URL_SAT}/GetUserFCM?Username={user}").text
    return resp

def addUser(user:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/CreateUser", data={"Username":user}).text

def createSession(user:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/CreateSession", data={"Username":user}).text
    return resp

def joinSession(user:str, sessionID:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/JoinSession", data={"Username":user, "SessionID":sessionID}).text
    return resp == "true"

def uploadImage(image:str, sessionID:str):
    resp = requests.post(f"{const.BASE_URL_SAT}/UploadImage", data={"Image":image, "SessionID":sessionID}).text
    return resp == "true"

def getSessionUsers(sessionID:str):
    resp = requests.get(f"{const.BASE_URL_SAT}/GetSessionUsers?SessionID={sessionID}").json()
    return resp

def getSessionImages(sessionID:str):
    resp = requests.get(f"{const.BASE_URL_SAT}/GetSessionImages?SessionID={sessionID}").json()
    return resp

def leaveSession(user, sessionID:str):
    resp = requests.request("DELETE",f"{const.BASE_URL_SAT}/LeaveSession", data={"Username":user}).text
    return resp == "true"

def inviteFriend(user:str, friend:str, sessionID:str):
    friends = getFriends(user)
    if friend in friends:
        notify(user, getFMC(friend), sessionID)
        return True
    return False

def notifyImage(user:str, users:list, imageID:str):
    for i in users:
        if i != user:
            uploadToUser(getFMC(i), imageID)

def uploadToUser(fmc:str, imageID:str):
    if fmc == "":
        return False
    message = messaging.Message(
        notification=messaging.Notification(title="NEW IMAGE", body=imageID),
        data={"imageID":imageID},
        token=fmc
    )
    response = messaging.send(message)

    return True


def notify(user:str, fmc:str, sessionID:str):
    if fmc == "":
        return False
    message = messaging.Message(
        notification=messaging.Notification(title="INVITATION FROM PHOT.ON USER", body=f"{user} has invited you to a session"),
        data={"sessionID":sessionID},
        token=fmc
    )
    response = messaging.send(message)

    return True