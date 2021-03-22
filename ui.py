from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.simpledialog import askstring
from tkinter.filedialog import asksaveasfilename, askopenfilename
from pageBrain import PageBrain
from cryptography.fernet import InvalidToken
from os import path
from pathlib import Path
import shutil
from pathlib import Path
from dropboxUtility import isLinkedToDBBefore, obtainDropboxAuthFlow, saveLocalRefreshToken, isFileExistsAtDBRoot, uploadFileAtDBRoot, isLinkedToDBBefore
import webbrowser
import json

import random
import pyperclip  # third party library

#------------------------- Constants -----------------------------#
# for password generation
LETTERS = list("abcdefghijklmnopqrstuvwxyz")
NUMBERS = list("0123456789")
SYMBOLS = list("!#$%&()*+")

#------------------------- Menu Labels ---------------------------#
LINKDROPBOX = "Link to Dropbox"
BACKUPTODROPBOX = "Backup Vault to Dropbox"

class MainWindow:
    def __init__(self):

        self.window = Tk()
        # self.window.geometry("400x400+100+100")
        self.window.minsize(width=400, height=350)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        self.window.title("Password Manager")
        self.window.config(padx=2, bg="white")

        # menu - file
        menubar = Menu(self.window, bg="white")
        filemenu = Menu(menubar, tearoff=False)

        filemenu.add_command(label="Save As", command=self.renameVaultFile)
        filemenu.add_command(label="Open", command=self.openFrameWithPage)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        # menu - tools cascade
        self.toolMenu = Menu(menubar, tearoff=False)
        self.toolMenu.add_command(label=LINKDROPBOX, command=self.logInDropbox)
        self.toolMenu.add_command(label=BACKUPTODROPBOX, command=self.backup)
        menubar.add_cascade(label = "Tools", menu=self.toolMenu)
        self.window.config(menu=menubar)
        self._uIActionsIfLinkedToDB() # enable/ disable menu for DB based on linked statuss

        # frame
        self.currFrame = SimpleFormIconFrame()
        self.currFrame.grid(row=0, column=0)

        self._createVaultFolder()

        self.window.mainloop()

    # Helpers

    def _uIActionsIfLinkedToDB(self):
        if isLinkedToDBBefore():
            self._disableMenuItem(self.toolMenu, LINKDROPBOX)
            self._enableMenuItem(self.toolMenu, BACKUPTODROPBOX)
        else:
            self._enableMenuItem(self.toolMenu, LINKDROPBOX)
            self._disableMenuItem(self.toolMenu, BACKUPTODROPBOX)


    def _disableMenuItem(self, menu, itemName=None):
        if itemName == None:
            return
        menu.entryconfig(itemName, state="disabled")
        
    def _enableMenuItem(self, menu, itemName=None):
        if itemName == None:
            return
        menu.entryconfig(itemName, state="normal")


    def _createVaultFolder(self):
        folderPath = "./vault"
        Path(folderPath).mkdir(parents=True, exist_ok=True)

    # Callbacks - Commands

    def logInDropbox(self):
        auth_flow = obtainDropboxAuthFlow()
        
        authorize_url = auth_flow.start()
        #print("1. Go to: " + authorize_url)
        #print("2. Click \"Allow\" (you might have to log in first).")
        #print("3. Copy the authorization code.")
        webbrowser.open_new_tab(authorize_url)

        auth_code = simpledialog.askstring(title="Authorization Code", prompt="Enter the Dropbox Authorization Code:")
        if auth_code:
            auth_code.strip()
        else:
            messagebox.showerror(title="Error Authorization Code", message="Check your Authorization Code")
            return    

        try:
            oauth_result = auth_flow.finish(auth_code)
            #print(oauth_result)
        except Exception as e:
            #print('Error: %s' % (e,))
            messagebox.showerror(title="Error Linking Dropbox", message="Unable to complete Dropbox OAuth")            
        else:
            #save token
            saveLocalRefreshToken(oauth_result.refresh_token)
            self._uIActionsIfLinkedToDB() # enable / disable menu related to DB based on link status

        return


    def backup(self):
        if isinstance(self.currFrame, FormFrame) == False:
            messagebox.showwarning(title="Backup", message="No page to backup!")
            return
        
        currentPageBrain = self.currFrame.pageBrain

        # Check page file exists on DB, is yes ask User to proceed.
        dbFilePath = f"/{Path(currentPageBrain.fullFileName).name}"
        if isFileExistsAtDBRoot(dbFilePath):
            answer = messagebox.askyesno(title="Dropbox", message="Overwrite page file in Dropbox?")
            if answer == False:
                return

        # Upload page file to DB
        if uploadFileAtDBRoot(dbFilePath, currentPageBrain.fullFileName) == False:
            messagebox.showerror(title="Error", message="Page file not uploaded to Dropbox")
        else:
            messagebox.showinfo(title="Success", message="Uploaded Page File to Dropbox.")
        
        return
        
    def openFrameWithPage(self):
        defaultPageName = "./vault/data.json"
        pageName = defaultPageName
        fileName = askopenfilename(initialdir="./vault",
                                   filetypes=(("JSON Files", ".json"),))
        if fileName:
            pageName = fileName
        else:
            messagebox.showinfo(title="No file selected",
                                message="Default page file will be used")

        pageBrain = PageBrain(pageName)
        if self.currFrame:
            self.currFrame.destroy()
        self.currFrame = FormFrame(self.window, pageBrain)
        self.currFrame.grid(row=0, column=0)
        self.window.resizable(False, False)

    def renameVaultFile(self):
        if self.currFrame == None:
            messagebox.showerror(title="No page opened",
                                 message="Cannot save!")
            return

        fileName = asksaveasfilename(initialdir="./vault",
                                     title="Save Page File As",
                                     filetypes=(("JSON Files", ".json"),))

        if fileName:
            if not fileName.endswith(".json"):
                fileName = f"{fileName}.json"

        dest = path.normpath(fileName)
        source = path.normpath(path.abspath(
            self.currFrame.pageBrain.fullFileName))
        if dest != source:  # not the same
            try:
                shutil.move(source, dest)
            except FileNotFoundError:
                messagebox.showerror(title="File not saved",
                                     message="Error in moving file")
            else:
                self.currFrame.pageBrain.fullFileName = dest


class SimpleFormIconFrame(Frame):
    def __init__(self):
        Frame.__init__(self, bg="white")

        self.canvas = Canvas(self, width=330, height=330,
                             bg="white", highlightthickness=0)

        self.logoImage = PhotoImage(file="./safe.png")
        self.canvas.create_image(165, 165, image=self.logoImage)
        self.canvas.grid(row=0, column=0)


class FormFrame(Frame):
    def __init__(self, parent: Tk, page: PageBrain):
        Frame.__init__(self, parent, bg="white")

        self.pageBrain = page

        self.canvas = Canvas(self, width=200, height=200,
                             bg="white", highlightthickness=0)

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
        self.statusLabel = Label(
            self, text="", fg="grey", bg="white", relief=SUNKEN, anchor=E, width=60)
        self.statusLabel.grid(column=0, row=5, sticky=W+E,
                              columnspan=3, pady=(50, 2))

        # entries
        self.website = StringVar()  # using string val so that can monitor it
        # track the string var
        self.website.trace_add("write", self.websiteChangedFindWord)
        self.websiteEntry = Entry(self, width=18, textvariable=self.website)
        self.websiteEntry.grid(column=1, row=1)
        self.websiteEntry.focus()

        self.emailUserEntry = Entry(self, width=38)
        self.emailUserEntry.grid(column=1, row=2, columnspan=2)

        self.passwordEntry = Entry(self, width=18)
        self.passwordEntry.grid(column=1, row=3)

        # buttons
        self.genPassButton = Button(
            self, text="Generate Password", bg="white", width=15)
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
            masterpw = askstring(title="Session Password",
                                 prompt="Enter Password")
            if len(masterpw):
                self.pageBrain.masterPassword = masterpw

    def generatePassword(self):
        num_letters = random.randint(8, 10)  # 8 to 10 letters
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

        is_okay = messagebox.askokcancel(
            title=websiteStr, message=f"These are the details:\nEmail: {emailUserStr}\nPassword: {passwordStr}\nIs it okay to save?")

        if is_okay:
            self.pageBrain.saveToFile(websiteStr, emailUserStr, passwordStr)

            # clear fields after saving
            self.website.set("")
            self.emailUserEntry.delete(0, END)
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
                # re-ask for session password
                masterpw = askstring(
                    title="Wrong Session Password", prompt="Enter Password")
                if len(masterpw):
                    self.pageBrain.masterPassword = masterpw
            else:
                msg = f"Email/User: {userEmailPlain}\nPassword: {passwordPlain}"
                messagebox.showinfo(title=trimmedSearchWord,
                                    message=msg, icon="info")
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
            self._searchWordsWithPrefix(
                prefixedTrie[chr], suffix+chr, foundwords, countLimit)
            if countLimit == len(foundwords):
                break
