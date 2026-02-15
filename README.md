# Macro App

## Details
A simple automation tool for keyboard and mouse inputs. Allows record and playback functionality as well as manual editing afterwards. Supports hotkeys for starting and stopping. Can also save macros for later retrieval.

## Purpose
I made it mainly to automate some simple repetitive game tasks.

## How to Run
With python (and the relevant imports) installed, running the main.py file should work. I also used pyinstaller to bundle it into one executable which is another option, though the executable is not in this repo.
With pyinstaller, the command I used to bundle it on Windows was: pyinstaller --noconsole --onefile --icon=icon.ico --add-data "gui/icon.png;gui" main.py

## Status
It should be finished, though there may be some bugs that I haven't noticed. My testing wasn't extremely thorough. For basic usage it will work.
If I ever decide I want to add something in the future, I might come back, but for now I'm declaring it done.
