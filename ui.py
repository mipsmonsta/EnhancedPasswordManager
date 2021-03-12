from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter.simpledialog import askstring
from tkinter.filedialog import asksaveasfilename, askopenfilename
from pageBrain import PageBrain
from cryptography.fernet import InvalidToken
from os import path
import shutil
            

import random
import pyperclip # third party library

#------------------------- Constants -----------------------------#
# for password generation
LETTERS = list("abcdefghijklmnopqrstuvwxyz")
NUMBERS = list("0123456789")
SYMBOLS = list("!#$%&()*+")
        

class MainWindow:
    def __init__(self):
        
        self.window = Tk()
        #self.window.geometry("400x400+100+100")
        self.window.minsize(width=400, height=350)
       
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        
        self.window.title("Password Manager")
        self.window.config(padx=2, bg="white")
        
        # menu
        menubar = Menu(self.window, bg="white")
        filemenu = Menu(menubar, tearoff=False)

        filemenu.add_command(label="Save As", command=self.renameVaultFile)
        filemenu.add_command(label="Open", command=self.openFrameWithPage)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.window.config(menu=menubar)
        
        # frame
        self.currFrame = None
    
        self.window.mainloop() 
        
    def openFrameWithPage(self):
        defaultPageName = "./vault/data.json"
        pageName = defaultPageName
        fileName = askopenfilename(initialdir="./vault", 
                                   filetypes=(("JSON Files", ".json"),))
        if fileName:
            pageName = fileName
        else:
            messagebox.showinfo(title="No file selected", message="Default page file will be used")
        
        pageBrain = PageBrain(pageName)
        if self.currFrame:
            self.currFrame.destroy()
        self.currFrame = FormFrame(self.window, pageBrain)
        self.currFrame.grid(row=0, column=0)

    def renameVaultFile(self):
        if self.currFrame == None:
            messagebox.showerror(title="No page opened", message="Cannot save!")
            return
        
        fileName = asksaveasfilename(initialdir="./vault", 
                                     title="Save Page File As",
                                     filetypes=(("JSON Files", ".json"),))
        
        if fileName:
            if not fileName.endswith(".json"):
                fileName = f"{fileName}.json"
                
        dest = path.normpath(fileName)
        source = path.normpath(path.abspath(self.currFrame.pageBrain.fullFileName))
        if dest != source: # not the same
            try:
                shutil.move(source, dest)
            except FileNotFoundError:
                messagebox.showerror(title="File not saved", message="Error in moving file")
            else:
                self.currFrame.pageBrain.fullFileName = dest
                
                        
class FormFrame(Frame):
    def __init__(self, parent: Tk, page: PageBrain):
        Frame.__init__(self, parent, bg="white")

        self.pageBrain = page
        
        self.canvas = Canvas(self, width=200, height=200, bg="white", highlightthickness=0)
        
        self.logoImage = PhotoImage(file="./logo.png")
        self.canvas.create_image(100, 100, image=self.logoImage)
        self.canvas.grid(column=1, row=0)

        # labels
        self.websiteLabel = Label(self, text="Website:", bg="white")
        self.websiteLabel.grid(column=0, row=1)

        self.emailUserLabel = Label(self, text="Email/Username:", bg="white")
        self.emailUserLabel.grid(column=0, row=2)

        self.passwordLabel = Label(self, text="Password:", bg="white")
        self.passwordLabel.grid(column=0, row=3)

        # status bar using a label
        self.statusLabel = Label(self, text="", fg="grey", bg="white", relief=SUNKEN, anchor=E, width=60)
        self.statusLabel.grid(column=0, row=5, sticky=W+E, columnspan=3, pady=(50, 2))


        # entries
        self.website = StringVar() # using string val so that can monitor it
        self.website.trace_add("write", self.websiteChangedFindWord) # track the string var
        self.websiteEntry = Entry(self, width=18, textvariable=self.website)
        self.websiteEntry.grid(column=1, row=1)
        self.websiteEntry.focus()

        self.emailUserEntry = Entry(self, width=38)
        self.emailUserEntry.grid(column=1, row=2, columnspan=2)

        self.passwordEntry = Entry(self, width=18)
        self.passwordEntry.grid(column=1, row=3)

        # buttons
        self.genPassButton = Button(self, text="Generate Password", bg="white", width=15)
        self.genPassButton.config(command=self.generatePassword)
        self.genPassButton.grid(column=2, row=3, sticky=W)

        self.addPassButton = Button(self, text="Add", width=36, bg="white")
        self.addPassButton.config(command=self.save)
        self.addPassButton.grid(column=1, row=4, columnspan=2)

        self.searchButton = Button(self, text="Search", bg="white", width=15)
        self.searchButton.config(command=self.searchPassword)
        self.searchButton.grid(column=2, row=1, sticky=W)
        
        # after 1 sec, ask user for password for page
        parent.after(1000, self.setMasterPassword)
      
    def setMasterPassword(self):
        if self.pageBrain.masterPassword == None:
            masterpw = askstring(title="Session Password", prompt="Enter Password")
            if len(masterpw):
                self.pageBrain.masterPassword = masterpw  
        
    def generatePassword(self):
        num_letters = random.randint(8, 10) # 8 to 10 letters
        num_symbols = random.randint(2, 4)  # 2 to 4 symbols
        num_numbers = random.randint(2, 4)  # 2 to 4 numbers
        chosenLetters = random.choices(LETTERS, k=num_letters)
        chosenSymbols = random.choices(SYMBOLS, k=num_symbols)
        chosenNumbers = random.choices(NUMBERS, k=num_numbers)
        
        password = chosenLetters + chosenSymbols + chosenNumbers
        random.shuffle(password)
        
        genPasswordStr = "".join(password)
        self.passwordEntry.delete(0, END)
        self.passwordEntry.insert(0, genPasswordStr)
    
    def save(self):
        
        websiteStr = self.website.get().strip()
        emailUserStr = self.emailUserEntry.get().strip()
        passwordStr = self.passwordEntry.get().strip()

        if len(websiteStr) == 0 or len(emailUserStr) == 0 or len(passwordStr) == 0:
            msg = "Please do not leave any fields empty"
            messagebox.showinfo(title="Oops", message=msg, icon="warning")
            return

        is_okay = messagebox.askokcancel(title=websiteStr, message=f"These are the details:\nEmail: {emailUserStr}\nPassword: {passwordStr}\nIs it okay to save?")
            
        if is_okay:
            self.pageBrain.saveToFile(websiteStr, emailUserStr, passwordStr)
            
            # clear fields after saving
            self.website.set("")
            self.emailUserEntry.delete(0,END)
            self.passwordEntry.delete(0, END)

    def searchPassword(self):
        searchWord = self.website.get()
        if len(searchWord) == 0:
            return
        
        # Read json
        trimmedSearchWord = searchWord.strip()
            
        if trimmedSearchWord in self.pageBrain.jsonDict['data']:
            userEmailCipher = self.pageBrain.jsonDict['data'][trimmedSearchWord]["emailUser"]
            passwordCipher = self.pageBrain.jsonDict['data'][trimmedSearchWord]['password']
            
            try:    
                userEmailPlain = self.pageBrain.decrypt(userEmailCipher)
                passwordPlain = self.pageBrain.decrypt(passwordCipher)
            except InvalidToken:
                #re-ask for session password
                masterpw = askstring(title="Wrong Session Password", prompt="Enter Password")
                if len(masterpw):
                    self.pageBrain.masterPassword = masterpw
            else:
                msg = f"Email/User: {userEmailPlain}\nPassword: {passwordPlain}"
                messagebox.showinfo(title=trimmedSearchWord, message=msg, icon="info")
                pyperclip.copy(passwordPlain)
    
    def websiteChangedFindWord(self, *args):
       
        websiteStr = self.website.get().strip()
        
        if len(websiteStr) == 0:
            self.statusLabel.config(text="")
            return
        
        t = self.pageBrain.trie
        
        for chr in websiteStr:
            if chr in t:
                t = t[chr]
            else:
                self.statusLabel.config(text="")
                return
        foundWords = []
        countLimit = 3
        self._searchWordsWithPrefix(t, websiteStr, foundWords, countLimit)
       
        self.statusLabel.config(text=" | ".join(foundWords))
     
    
    
    def _searchWordsWithPrefix(self, prefixedTrie, suffix, foundwords, countLimit):
        if '#' in prefixedTrie:
            foundwords.append(suffix)
            if countLimit == len(foundwords):
                return

        for chr in (set(prefixedTrie.keys()) - set(['#'])):
            self._searchWordsWithPrefix(prefixedTrie[chr], suffix+chr, foundwords, countLimit)
            if countLimit == len(foundwords):
                break   
   