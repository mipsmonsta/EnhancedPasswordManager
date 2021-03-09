from tkinter import *
from tkinter import messagebox
from pageBrain import PageBrain
import random
import pyperclip # third party library


class MainWindow:
    def __init__(self):
        
        self.window = Tk()
        self.window.title("Password Manager")
        self.window.config(padx=2, bg="white")
        
        # menu
        menubar = Menu(self.window, bg="white")
        filemenu = Menu(menubar, tearoff=0)

        filemenu.add_command(label="Exit", command=self.window.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.window.config(menu=menubar)
        
        #pageBrain 
        pageBrain = PageBrain("data")
        
        # frame
        self.currFrame = FormFrame(self.window, pageBrain)
        self.currFrame.grid(row=0, column=1)
    
        self.window.mainloop() 
        
class FormFrame(Frame):
    def __init__(self, parent, page: PageBrain):
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
        
        # for password generation
        self.letters = list("abcdefghijklmnopqrstuvwxyz")
        self.numbers = list("0123456789")
        self.symbols = list("!#$%&()*+")
        
    def generatePassword(self):
        num_letters = random.randint(8, 10) # 8 to 10 letters
        num_symbols = random.randint(2, 4)  # 2 to 4 symbols
        num_numbers = random.randint(2, 4)  # 2 to 4 numbers
        chosenLetters = random.choices(self.letters, k=num_letters)
        chosenSymbols = random.choices(self.symbols, k=num_symbols)
        chosenNumbers = random.choices(self.numbers, k=num_numbers)
        
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
            msg = f"Email/User: {self.pageBrain.jsonDict['data'][trimmedSearchWord]['emailUser']}\nPassword: {self.pageBrain.jsonDict['data'][trimmedSearchWord]['password']}"
            messagebox.showinfo(title=trimmedSearchWord, message=msg, icon="info")
            pyperclip.copy(self.pageBrain.jsonDict['data'][trimmedSearchWord]['password'])
    
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
   