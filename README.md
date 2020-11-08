#Boost
Hi, thanks for checking out Boost!
We're proud to announce that we won the Maverick Category at HackRU 2020 Fall, here's our DevPost: https://devpost.com/software/boost-ifdewk
Anyway, if you'd like to try Boost for yourself, here's everything you'll need to do:
1. Download all contents of the github by selecting download as zip, then extract it somehwere on your computer
2. Download and install Python with "sudo apt-get install Python3" on Linux or download and run the installer for Windows, I'd recommend selecting the option "Add variable to path" which allows Python to be run in any directory
3. Next up, Boost has some dependencies that it imports at the top, you'll probably have to install them: pygame, neat-python, pickle, pynput, inputs. This can be done with the command pip install pygame, etc, or maybe pip3 if you installed python3. Pip should come installed with Python, if not you can find installation instructions online
4. Now you're ready to run Boost. From our testing, the mainMenu.py file only works properly on Windows, and you can run "Python mainMenu.py" in a command prompt in the Boost directory, from here you can select some options. 
-For my Linux friends or those having issues, racertest.py is the file to run. Running "Python racertest.py" will begin training Boost on the map currently in the directory. To draw a new map, type "Python racertest.py 2", which will bring up the map creation tool, from here just select at least 3 points to draw a map, then press 'q' to save and close. To drive around yourself, run "Python racertest.py 1", which won't run the AI, and allows you to control a car with WASD. 

Leave us a comment on Devpost if you enjoyed our project or if you have any issues, and as always, happy hacking!