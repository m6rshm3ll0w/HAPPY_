import sys

from MODULES.BACKGROUND.deadline_task_notification import notification2
from MODULES.BACKGROUND.strike_notification import notification1
from dotenv import dotenv_values

# получение данных из файла globals.txt
try:
    config = dotenv_values("./DATA/globals.txt")
    VERSION = config["version"]
    By = config["by"]
except Exception as e:
    # без него программа не запустится
    print(f".env error: {e}")
    sys.exit()


# запуск функций уведомления
def init_all():
    notification1.start()
    notification2.start()
