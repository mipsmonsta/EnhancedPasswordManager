# Enhanced Password Manager

This repo is cross-platform (Windows/mac/Linux) GUI Password Manager written in Python and Tkinter.

## Features

- Suggests passwords so you won't have to roll your own weak ones
- Local storage of passwords with Symmetric Encryption
- Salt based encryption for added strength of stored passwords
- Create different "domain" pages to store different categories of passwords
- 100% Python codes - so you can audit what the code is doing and use the app with peace of mind

TODO - store vault page files in dropbox

### Usage

Firstly clone this repo with

```
$ git clone https://github.com/mipsmonsta/EnhancedPasswordManager
```

Use menu: File > Open and Cancel to create a default page named data.json.

When prompted set password for the page. This password is used to encrypt the stored passwords.
It will not be stored, hence don't forget it! There is no recovery if this password is lost.

To rename the page to a different filename, use menu: Save As. E.g. "data.json" to "work.json".
You can create diffferent filenames for different "domains", this way.

### Backing Up Your Pages

The pages are stored in relative folder:

```
./vault/<pagename>.json
```

The vault folder is created automatically. You can just keep copies of the pages, i.e. you are very much in control.
