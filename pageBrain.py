import json
from datetime import datetime as dt

class PageBrain:
    
    
    def __init__(self, fileName):
        self.fullFileName = f"./vault/{fileName}.json"
        self.jsonDict = None
        self.trie = None
        self._loadFromFile()
        
    def _loadFromFile(self):
        try:
            with open(self.fullFileName) as reader:
                self.jsonDict = json.load(reader)
        except FileNotFoundError:
            self.jsonDict = {"metadata":{"created": f"{dt.now().isoformat()}"}, 
                             "data": {}}
            with open(self.fullFileName, "w") as writer:
                json.dump(self.jsonDict, writer, indent=4)
                
        self._readDataBuildTrie()
                
    def saveToFile(self, website: str, user: str, password: str):
        newData = {website:{"emailUser": user, "password": password, "modified": f"{dt.now().isoformat()}"}}
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
    
    

        
        
        
    