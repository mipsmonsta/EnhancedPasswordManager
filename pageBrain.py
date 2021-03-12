import json
from datetime import datetime as dt

#imports for encryption
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class PageBrain:
    
    def __init__(self, fileName):
        self.fullFileName = fileName
        self.jsonDict = None
        self.trie = None
        self._masterPassword = None
        self._loadFromFile()
        
    def _loadFromFile(self):
        try:
            with open(self.fullFileName) as reader:
                self.jsonDict = json.load(reader)
        except FileNotFoundError:
            base64_msg = base64.b64encode(os.urandom(16)).decode("utf-8")
            
            self.jsonDict = {"metadata":{"created": f"{dt.now().isoformat()}"}, 
                             "data": {}, "salt": base64_msg}
            
            with open(self.fullFileName, "w") as writer:
                json.dump(self.jsonDict, writer, indent=4)
                
        self._readDataBuildTrie()
                
    def saveToFile(self, website: str, user: str, password: str):
        userCipher = self.encrypt(user)
        passwordCipher = self.encrypt(password)
        newData = {website:{"emailUser": userCipher, "password": passwordCipher, "modified": f"{dt.now().isoformat()}"}}
        self.jsonDict["data"].update(newData)
        with open(self.fullFileName, "w") as writer:
            json.dump(self.jsonDict, writer, indent=4)
        self._readDataBuildTrie()
    
    def _readDataBuildTrie(self):
        self.trie = {}
        for word in self.jsonDict["data"].keys():
            t = self.trie
            for chr in word:                    
                if chr not in t:
                    t[chr] = {}
                
                t = t[chr]
            t['#'] = '#'
            
    def _getSalt(self)-> bytes:
        base64_str = self.jsonDict["salt"].encode("utf-8")
        return base64.b64decode(base64_str) #bytes     
            
    @property
    def masterPassword(self):
        return self._masterPassword
    
    @masterPassword.setter
    def masterPassword(self, newMasterPassword):
        passwordBytes = newMasterPassword.encode("utf-8")

        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=self._getSalt(), iterations=100000)
        key = base64.urlsafe_b64encode(kdf.derive(passwordBytes))
        self._masterPassword = key
        
    def encrypt(self, plainText:str):
        f = Fernet(self._masterPassword)
        return base64.b64encode(f.encrypt(plainText.encode("utf-8"))).decode("utf-8")
                                
    def decrypt(self, cipher:str):
        f = Fernet(self._masterPassword)
        token = base64.b64decode(cipher.encode("utf-8"))
        
        plainText = f.decrypt(token).decode("utf-8")
            
        return plainText
        
        
        
    
    

        
        
        
    