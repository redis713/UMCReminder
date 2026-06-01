import webview
import winsound
import requests
import time
import os
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return filename

SOUND_PATH = resource_path("s1.wav")
API_URL_INFO = "http://umcreminder.umcgochs.local/api/get_client_info"
API_URL_ALERT_WINDOW = "http://umcreminder.umcgochs.local/alert_window"
API_URL_TASKS = "http://umcreminder.umcgochs.local/api/tasks"

DEFAULT_CHECK_INTERVAL = 10800  # 2 часа в секундах
CHECK_INTERVAL = 10800

DEFAULT_WIDTH = 1000
WIDTH = 1000

DEFAULT_HEIGHT = 800
HEIGHT = 800

DEFAULT_TITLE = "Напоминалки"
TITLE = "Напоминалки"


try:
    r = requests.get(API_URL_INFO, verify=False, timeout=5)
    data = r.json()

    CHECK_INTERVAL = data.get("check_interval", DEFAULT_CHECK_INTERVAL)
    WIDTH = data.get("width", DEFAULT_WIDTH)
    HEIGHT = data.get("height", DEFAULT_HEIGHT)
    TITLE = data.get("title", DEFAULT_TITLE)

except (requests.RequestException, ValueError) as e:
    print("Ошибка:", e)
    CHECK_INTERVAL = DEFAULT_CHECK_INTERVAL
    WIDTH = DEFAULT_WIDTH
    HEIGHT = DEFAULT_HEIGHT



def show_alert_window():
    window = webview.create_window(
        TITLE,
        API_URL_ALERT_WINDOW,
        width=WIDTH,
        height=HEIGHT,
        on_top=True
    )

    winsound.PlaySound("s1.wav", winsound.SND_ASYNC)
    webview.start()


def check_tasks():
    try:
        req = requests.get(API_URL_TASKS, verify=False, timeout=5)
        tasks_data = r.json()

        if tasks_data:
            show_alert_window()

    except Exception as e:
        print("Ошибка:", e)


def loop():
    while True:
        #print(CHECK_INTERVAL, API_URL_INFO)
        check_tasks()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    loop()


# for converting in exe: pyinstaller --onefile --noconsole webview_client.py --add-data "s1.wav;."

