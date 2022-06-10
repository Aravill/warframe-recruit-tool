import cv2, pyperclip, pyautogui, threading, subprocess, windowsapps, time, configparser, subprocess
import pytesseract
from pynput import keyboard
from datetime import date
from os import system, path
from playsound import playsound

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
class LogFileHandler:
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
        try:
            self.f = open(self.file_path, "w+")
        except:
            print(bcolors.FAIL + "Failed to load the log file directory, please check the directory exists: " + log_dir + bcolors.ENDC)
            quit()
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
def generate_default_config(config):
    config["general"] = {
        "tesseract_directory": r"C:\Program Files\Tesseract-OCR\tesseract",
        "recruit_log_directory": "logs"
    }
    config["keybinds"] = {
        "get_username":"<alt>+1",
        "search_in_discord":"<alt>+2",
        "register_recruit":"<alt>+3",
        "open_session_file":"<alt>+4",
        "refresh":"<alt>+r",
        "exit":"<alt>+q"
    }

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
    try:
        return pytesseract.image_to_string(more_readable_image(image)).strip()
    except:
        print(bcolors.FAIL + "Failed to launch tesseract, please check your installation directory: " + tesseract_dir + bcolors.ENDC)
        quit()

# -- LOADING CONFIG --
# Attempt to load if file exists, otherwise generate new one
config = configparser.ConfigParser()
if path.exists("config.ini"):
    config.read("config.ini")
else:
    generate_default_config(config)
    f = open("config.ini", "w")
    config.write(f)
    f.close()

# Reading recruit log directory
log_dir = config['general']['recruit_log_directory']
log_file_name = "recruiting_" + friendly_date().replace("/", "-") + ".txt"
# Reading tessecart directory and loading tesseract
tesseract_dir = config['general']['tesseract_directory']
try:
    pytesseract.pytesseract.tesseract_cmd = r""+tesseract_dir
except:
    print(bcolors.FAIL + "Failed to load tesseract, please check your installation directory: " + tesseract_dir + bcolors.ENDC)
    quit()

# -- PUBLIC VARIABLES --
# Loading in the image
template = cv2.imread('assets/template.png', cv2.IMREAD_UNCHANGED)
stat = Status()
rend = Renderer(stat)
separator = "	"

fhnd = LogFileHandler(path.join(log_dir, log_file_name), separator, stat)
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
    try:
        subprocess.Popen(["notepad.exe", path.join(log_dir, log_file_name)])
    except:
        print(bcolors.FAIL + "Failed to open the log file directory, please check the file exists: " + path.join(log_dir, log_file_name) + bcolors.ENDC)

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
    methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR, cv2.TM_CCORR_NORMED]
    
    found = False
    mi = 0
    name = ""
    while found == False and mi < len(methods):
        # print("using method %d", mi)
        match = cv2.matchTemplate(img2, active_box_template, methods[mi], mask=alpha)
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

        height, width = cropped_image.shape[:2]
        if width < height * 1.3:
            # Not recognized using current method
            mi += 1
            continue

        # cv2.rectangle(img2, top_left, bottom_right, 255, 4)

        #Image recognition part
        name = recognize_text(cropped_image)

        if len(name) < 1:
            # Not recognized using current method
            mi += 1
            continue

        found = True
    
    if len(name) < 1:
        print(bcolors.FAIL + "Username not recognized!" + bcolors.ENDC)
        return

    pyperclip.copy(name)
    stat.update_current_user(name)
    rend.refresh()
    playsound('assets/sound.mp3')

# Reading keybinds
function_map = {
    "get_username": async_get_username,
    "search_in_discord": async_search_in_discord,
    "register_recruit": async_register_recruit,
    "open_session_file": async_open_session_file,
    "refresh": async_refresh,
    "exit": the_end
}
keybinds = {}
for kb in config['keybinds']:
        keybinds[config['keybinds'][kb]] = function_map[kb] 

# -- HOTKEY REGISTRATION --
with keyboard.GlobalHotKeys(keybinds) as h:
    h.join()