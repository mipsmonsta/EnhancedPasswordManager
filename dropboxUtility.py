import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from appkey import DB_APP_KEY
import webbrowser

def obtainDropboxRefreshToken():
    auth_flow = DropboxOAuth2FlowNoRedirect(DB_APP_KEY, use_pkce=True, token_access_type='offline')

    authorize_url = auth_flow.start()
    #print("1. Go to: " + authorize_url)
    #print("2. Click \"Allow\" (you might have to log in first).")
    #print("3. Copy the authorization code.")
    webbrowser.open_new_tab(authorize_url)


    auth_code = input("Enter the authorization code here:").strip()

    try:
        oauth_result = auth_flow.finish(auth_code)
        print(oauth_result)
    except Exception as e:
        print('Error: %s' % (e,))
        exit(1)
    else:
        return oauth_result.refresh_token