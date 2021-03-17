# Enhanced Password Manager

This repo is cross-platform (Windows/mac/Linux) GUI Password Manager written in Python and Tkinter.

## Features

- Suggests passwords so you won't have to roll your own weak ones
- Local storage of passwords with Symmetric Encryption
- Salt based encryption for added strength of stored passwords
- Create different "domain" pages to store different categories of passwords

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
