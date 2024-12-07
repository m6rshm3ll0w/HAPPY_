import datetime
import threading
import time

from MODULES.MESSAGE_CREATOR import show_mesage
from MODULES.BD.init import DB_connection

UPDATE_TIME = 1*60*60  # время обновления


def task_not_compleated():
    # подключение к бд
    db = DB_connection("./DATA/Dbase.db3")
    while True:
        # получение настроек
        static = db.db_get_settings()
        t_m = static[2]
        enable = static[3]

        # если включено
        if enable == 1:
            tasks = db.get_tasks(notif=True)  # получение не уведомленных задач

            # выполнение действий для каждой задачи
            for task in tasks:
                # получение сегодняшнего дня и дедлайна задачи
                today = str(datetime.date.today()).split("-")
                deadline = task[1].split("-")

                # если до дедлайна меньше назначенного времени, то запускаем уведомление
                if today[0] == deadline[0] and today[1] == deadline[1] and int(deadline[2]) - int(today[2]) <= t_m:
                    show_mesage(title="Напоминание: HaPPy", msg="напоминаем вам о незавершенной задаче")
                    db.notif_task(task[0])
                    # ждем, пока уведомление пропадет, если несколько задач
                    time.sleep(25)

        # ждем час
        time.sleep(UPDATE_TIME)


# создание фонового процесса
notification2 = threading.Thread(target=task_not_compleated)