# Warframe Recruiting Tool

## Description

This is a helper tool for the Darkstar Gladiators clan to aid with the recruitment process by offering player registration and lookup features.

### What this tool is

A macro which uses OCR to pull a player's username from an active chat tab and inserts it into the clipboard, allowing the recruiter to paste it wherever they need, look the user up on discord or register the user as recruited into a log file. This tool is made to fit the Darkstar Gladiators recruitment process as of 29.05.2022.

### What this tool isn't

A fully automated tool which would recruit players for the recruiter.

### Is it against Warframe or Discord ToS

No, the tool doesn't interact with Warframe or its code in any way, it simply takes a screenshot of the main system screen and attempts to find a specific pattern in it. As for discord, the tool only brings it into the foreground and pastes the player's username into the search box. This tool is just a macro with OCR (optical character recognition) capability.

## Installation

### Tesseract

In order for this tool to work, you will need to install Tesseract, this is the OCR software behind the username recognition. Download Tesseract [here](https://github.com/UB-Mannheim/tesseract/wiki).

### Recruiting tool

Download the latest recruiting tool release from this repository's releases page [here](https://github.com/Aravill/warframe-recruit-tool/releases). Unzip it using 7zip or WinRar, then open the `config.ini` file and adjust `tesseract_directory` path depending on where you installed Tesseract. You may also adjust the log file directory (by default it is `logs` inside the root application directory) or the application keybinds. Then launch the application by double clicking the `app.exe` executable.

## Features

### GUI

The tool is a console application, there is no other GUI at the moment nor do I plan to include one as I don't currently find it necessary.

### Username copying and pasting

The main reason this tool was created. Warframe doesn't offer a username copy feature which makes looking that username up on discord or registering it into a recruitment sheet slightly annoying. Once the username is recognized, the tool plays a notification sound.

### Username lookup on discord

Once the username is in the clipboard, the tool can "alt tab" to a running discord instance and attempt to look the username up in the active server (or DMs). In order for this feature to work properly, the "Pantsgrab Parade" server **must be active**. The tool cannot switch between servers or DMs.

### Session recruitment log

Once the user is recruited, the tool can log the user as recruited into a simple text log file, allowing the recruiter to go on and recruit more people without the need to register the user into the Darkstar Gladiators recruitment sheet right away. The text file is also formatted in a way that allows a convenient copy-paste from the log into the sheet later once the recruitment session is over. Once the username is saved, the tool plays a notification sound.

### Opening the session recruitment log

If any adjustment to the log needs to be made (for example the tool made an error in the username), the tool can open the session log in the notepad text editor to allow for quick adjustment.

### Refreshing the session recruitment log

If the session log file was edited, it is necessary to refresh the tool to see the new values in it.

## Tool configuration

Some features of the recruiting tool are configurable. All configurable variables are stored in the `config.ini` file. If the file is deleted, the tool will create a new one on startup.

### Tesseract directory

The tool uses Tesseract, an OCR software, to recognize usernames on an image. Adjust the `tesseract_directory` variable to point to Tesseract's installation directory.

### Log directory

This is the directory where the tool will create recruiting session logs containing the usernames of recruited players. By default, this is the `logs` directory in the application directory. You may change this using the `recruit_log_directory` variable

### Keybinds

These are the default tool keybinds, they can be adjusted by editing the `config.ini` file

```
alt+1: copy username
alt+2: lookup username in active discord server
alt+3: log user as recruited
alt+4: open recruitment log file
alt+r: refresh recruitment log
alt+q: exit tool
```

## Example

![Alt text](/assets/example.png?raw=true "Example")
