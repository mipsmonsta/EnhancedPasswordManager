import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from dropbox import exceptions, files
from appkey import DB_APP_KEY
import json
import os, datetime, time

REFRESH_JSON_PATH = "./.dbjson"

def obtainDropboxAuthFlow():
    return DropboxOAuth2FlowNoRedirect(DB_APP_KEY, use_pkce=True, token_access_type='offline')

def getLocalRefreskToken()-> str:
    dbTokenDict = None
    try:
        with open(REFRESH_JSON_PATH, "r") as reader:
            dbTokenDict = json.load(reader)
    except FileNotFoundError:
        return None
    
    return dbTokenDict["refresh"]

def saveLocalRefreshToken(token: str) -> bool:
    result = True

    dbTokenDict = {"refresh": token}
    try:
        with open(REFRESH_JSON_PATH, "w") as writer:
            json.dump(dbTokenDict, writer, indent = 4)
    except Exception:
        result = False
    finally:
        return result

def isFileExistsAtDBRoot(filePath: str) -> bool:
    result = True
    dbx = dropbox.Dropbox(oauth2_refresh_token=getLocalRefreskToken)
    try:
        dbx.files_get_metadata(filePath)
    except exceptions.ApiError:
        result = False
    finally:
        dbx.close()
    
    return result

def uploadFileAtDBRoot(filePath: str, localFilePath: str)-> bool:

    dbx = dropbox.Dropbox(oauth2_refresh_token=getLocalRefreskToken)
    mode = files.WriteMode.overwrite

    while "//" in filePath:
        filePath.replace("//", "/")

    mtime = os.path.getmtime(filePath)

    try:
        with open(localFilePath, "r") as reader:
            data = reader.read()
    except FileNotFoundError:
        dbx.close()
        return False

    try:
        dbx.files_upload(
            data, filePath, mode,
            client_modified=datetime.datetime(*time.gmtime(mtime)[:6]),
            mute=True)
    except exceptions.ApiError:
        dbx.close()
        return False

    return True


    
    

