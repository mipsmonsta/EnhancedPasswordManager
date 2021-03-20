import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from appkey import DB_APP_KEY

def obtainDropboxAuthFlow():
    return DropboxOAuth2FlowNoRedirect(DB_APP_KEY, use_pkce=True, token_access_type='offline')

