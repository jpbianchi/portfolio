import json

# with open('twiml-ai.json', 'r') as file:
#     podcast_info = json.load(file)

# print(type(podcast_info)) 

import os
print(f"Current working directory: {os.getcwd()}")
print(type(os.getcwd()))
print(os.getcwd().split('PORTFOLIO'))
print(os.getcwd().split('PORTFOLIO')[1])

from pathlib import Path
cwd=os.getcwd() 
print("cwd", cwd)
if 'PORTFOLIO' in cwd:
    curdir = cwd.split('PORTFOLIO')[1]
else:
    curdir = cwd.split('portfolio')[1]
pth = Path(curdir)
print("path", pth)
print("path image", (pth / 'bg-image.jpg'))