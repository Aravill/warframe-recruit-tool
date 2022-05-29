import pytesseract, cv2, pyperclip, pyautogui, threading, subprocess, windowsapps, time, configparser
from pynput import keyboard
from datetime import date
from os import system, path
from playsound import playsound
import subprocess

# -- CLI HANDLING --
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Renderer:
    def __init__(self, status):
        self.status = status

    def refresh(self):
        system("cls")
        print("User in clipboard: " + bcolors.OKGREEN + self.status.current_user + "\n" + bcolors.ENDC)
        print("Last recruits: ")
        last = 0
        if len(self.status.user_list) > 5:
            last = 5
        for record in self.status.user_list[-last:][::-1]:
            print(" • " + record.date + " | " + bcolors.OKCYAN + record.username + bcolors.ENDC)
        if len(self.status.user_list) > 5:
            print("... + " + bcolors.OKCYAN + str(len(self.status.user_list) - 5) + bcolors.ENDC)
        print("")
        print("Recruits total: " + bcolors.OKCYAN + str(len(self.status.user_list)) + bcolors.ENDC)

# -- FILE HANDLING --
class FileHandler:
    def __init__(self, file_path, separator, status):
        self.separator = separator
        self.status = status
        self.file_path = file_path
        if path.exists(file_path):
            self.status.populate_list(self.read_records())

    def read_records(self):
        self.f = open(self.file_path, "r")
        lines = self.f.readlines()
        records = []
        for l in lines:
            x = l.split(self.separator)
            records.append(Record(x[1].strip(), x[0].strip()))
        self.f.close()
        return records

    def close(self):
        if hasattr(self, 'f'):
            self.f.close()  

    def update_records(self):
        self.f = open(self.file_path, "w+")
        result = ""
        for r in self.status.user_list:
            result = result + r.date + "	" + r.username + "\n"
        self.f.write(result)
        self.f.flush()
        self.f.close()

# -- DATA STRUCTURES --
class Record:
    def __init__(self, username, date):
        self.username = username
        self.date = date

class Status:
    def __init__(self):
        self.current_user = ""
        self.user_list = []

    def append_user(self, username, date):
        self.user_list.append(Record(username, date))

    def update_current_user(self, username):
        self.current_user = username

    def populate_list(self, records):
        self.user_list = records

# -- HELPER FUNCTIONS --
def ctrl_keybind(key):
    pyautogui.keyDown('ctrl')
    time.sleep(.1)
    pyautogui.press(key)
    time.sleep(.1)
    pyautogui.keyUp('ctrl')

def ss_and_read():
    ss = pyautogui.screenshot()
    ss.save(r'assets/ss.jpg')
    img = cv2.imread('assets/ss.jpg', 0)
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

def friendly_date():
    timestamp = date.today()
    friendly_date = timestamp.strftime("%d/%m/%Y")
    return friendly_date

def more_readable_image(image):
    # Magic to make the test more readable
    # Increase size
    (h, w) = image.shape[:2]
    resized = cv2.resize(image, (w*6, h*6))
    # Grey scale
    gry = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # Invert for thresholding
    thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # Invert again
    inv = cv2.bitwise_not(thr)
    return inv

def recognize_text(image):
    pytesseract.pytesseract.tesseract_cmd = r""+tesseract_dir
    return pytesseract.image_to_string(more_readable_image(image)).strip()

# -- READING CONFIG --
config = configparser.ConfigParser()
config.read('config.ini')
# Reading keybinds
keybinds = {}
for kb in config['keybinds']:
    if kb == "exit":
        keybinds[config['keybinds'][kb]] = "the_end"
    else:
        keybinds[config['keybinds'][kb]] = "async_" + kb

# Reading tessecart directory
tesseract_dir = config['general']['tesseract_directory']

# -- PUBLIC VARIABLES --
template = cv2.imread('assets/template.png', cv2.IMREAD_UNCHANGED)
stat = Status()
rend = Renderer(stat)
session_file_name = "recruiting_" + friendly_date().replace("/", "-") + ".txt"
separator = "	"
fhnd = FileHandler(session_file_name, separator, stat)
rend.refresh()

# -- TRIGGER FUNCTIONS --
def async_search_in_discord():
    threading.Thread(target=search_in_discord).start()

def async_open_session_file():
    threading.Thread(target=open_session_file).start()

def async_get_username():
    threading.Thread(target=get_username).start()

def async_register_recruit():
    threading.Thread(target=register_recruit).start()

def async_refresh():
    threading.Thread(target=refresh).start()

def the_end():
    fhnd.close()
    quit()

# -- MAIN LOGIC --
def open_session_file():
    subprocess.Popen(["notepad.exe", session_file_name])

def search_in_discord():
    windowsapps.open_app('Discord')
    # Give discord enough time to pop up
    time.sleep(1)
    # Open search bar
    ctrl_keybind('f')
    # Delete channel filter
    ctrl_keybind('a')
    pyautogui.press('backspace')   
    # Ensure current user in clipboard
    pyperclip.copy(stat.current_user)
    # Paste username
    ctrl_keybind('v')
    # Search
    pyautogui.press('enter')

def refresh():
    stat.populate_list(fhnd.read_records())
    rend.refresh()

def register_recruit():
    f_date = friendly_date()
    username = stat.current_user
    stat.append_user(username, f_date)
    rend.refresh()
    fhnd.update_records()
    playsound('assets/sound.mp3')

def get_username():
    img = ss_and_read()
    h, w = template.shape[:2]

    # Filter out alpha zone
    active_box_template = template[:,:,0:3]
    alpha = template[:,:,3]
    alpha = cv2.merge([alpha,alpha,alpha])

    # Copy image and look for a match
    img2 = img.copy()
    match = cv2.matchTemplate(img2, active_box_template, cv2.TM_CCORR_NORMED, mask=alpha)

    # Match results
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)

    top_left = max_loc

    i = 0
    offset = 1
    pointer = (top_left[1] + offset, top_left[0] + offset + i, 2)
    while img2[pointer] > 60:
        i += 1
        pointer = (top_left[1] + offset, top_left[0] + offset + i, 2)

    # Get bottom right
    bottom_right = (pointer[1], top_left[1] + h)

    # Crop (playing with pixels here to remove the shading on the chat box edge)
    cropped_image = img2[top_left[1]+2:bottom_right[1]-2, top_left[0]+2:bottom_right[0]-2]

    #Image recognition part
    name = recognize_text(cropped_image)
    pyperclip.copy(name)
    stat.update_current_user(name)
    rend.refresh()
    playsound('assets/sound.mp3')

# -- HOTKEY REGISTRATION --
with keyboard.GlobalHotKeys({
        '<alt>+1': async_get_username,
        # '<alt>+2': async_search_in_discord,
        '<alt>+2': async_register_recruit,
        '<alt>+3': async_open_session_file,
        '<alt>+4': async_search_in_discord,
        # '<alt>+e': test,
        '<alt>+r': async_refresh,
        '<alt>+q': the_end}) as h:
    h.join()