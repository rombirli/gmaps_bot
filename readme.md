# gmaps bot : pyautogui & cv2 based bot for google maps
## how to use it
You must have a web browser opened on Google Maps on top. You can't use your computer while the bot is running. To stop it : ctrl alt del on windows
This script was tested on chrome 105 on Windows 11 with a screen of resolution 1920x1080, the zoom level in chrome was 100%.
It is written in *python3.10.7*

**If you don't have exactly the same settings you will have to replace all files in the directory templates (make your own screen-captures)***.
## sentences generation : 
The wordlist used to generate sentences is stored in sentences.txt.

If this file doesn't exist, it is downloaded from the link contained in the variable **comments_base_link**.

You can put any link from here http://textfiles.com/directory.html in this variable.
## results generation
you can enable or disable matching results generation by setting the variable **plot_figures** to True or False.
## removing your google maps comments
on google maps go to your contributions -> reviews 
 
launch bot_remove_all.py