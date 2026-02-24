# Canon Image Extractor
**Currently only works for Windows**

A tool designed to simplify and improve efficiency of ingesting Photographs or Videos from an external drive.

Finds every connected drive with DCIM folder at the root and automatically copying files to specified location and sorting them by date taken.
Find how to install if you're unfamiliar with python at the bottom.
## Usage
Will only extract from a drive if it has a file named "allow_save", added to prevent it trying to copy from drives you don't want it to.
Once python and the required libraries are installed you will need to open the .py file in a file editor and find the line **save_location = "C:/CanonImages/"** and change the directory to wherever you need!
Now you can double click the file to run it whenever you need it.

If you want it to run whenever an SD card is inserted you can do that using task scheduler however it'll run it whenever ANY device is connected. If you want to you can research that, but keep in mind if you don't know what the task scheduler does it's probably not worth the pain.
## Installation
To download the python file go to Releases and download the most recent version

In order to install this you need **python** installed and the following libraries:
- **pillow** (known as PIL in python)
- **piexif**

Install python from [python.org](https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe) **Make sure to click the tick box to add python to PATH**

Install libraries using Command Prompt and the command ```pip install pillow piexif```
