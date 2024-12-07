import sqlite3
from datetime import date
from typing import Union

from MODULES.MESSAGE_CREATOR import show_mesage


# класс базы данных
class DB_connection:
    # инициализация подключения к базе данных с возможностью выбора файла бд
    def __init__(self,
                 db_file: str = None):
        # подключение к бд
        print(f" > CONNECTING TO DB ......... ", end="")
        try:
            if not db_file:
                self.conn = sqlite3.connect("DATA/Dbase.db3", check_same_thread=False)
            else:
                self.conn = sqlite3.connect(db_file, check_same_thread=False)
            print("DONE")
        except Exception as Except_:
            print(Except_)
            exit()

        print(f" > CREATING DB CURSOR ....... ", end="")
        try:
            self.cursor = self.conn.cursor()
            print("DONE")
        except Exception as Except_:
            print(Except_)
            exit()

    # получение настроек и возвращение кортежа
    def db_get_settings(self,
                        get_strik: bool = False) -> tuple:
        if not get_strik:
            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("enable_messages",))
            msg_enable = self.cursor.fetchall()[0][0]

            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("message_timeout",))
            msg_timout = self.cursor.fetchall()[0][0]

            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("message_time_behind_deadline",))
            msg_deadline_timeout = self.cursor.fetchall()[0][0]

            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("messages_about_dont_completed_tasks",))
            msg_tasks = self.cursor.fetchall()[0][0]

            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("run_on_system_startup",))
            ru_st = self.cursor.fetchall()[0][0]

            return msg_enable, msg_timout, msg_deadline_timeout, msg_tasks, ru_st

        else:
            self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?", ("streak_day",))
            days = self.cursor.fetchall()[0][0]
            return days

    # запись настроек
    def settings_write(self,
                       msg_enable: bool,
                       msg_timout: int,
                       msg_deadline_timeout: int,
                       msg_tasks: bool, ru_st: int = None) -> None:
        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (0 if msg_enable is False else 1, "enable_messages",))

        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (msg_timout, "message_timeout",))

        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (msg_deadline_timeout, "message_time_behind_deadline",))

        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (0 if msg_tasks is False else 1, "messages_about_dont_completed_tasks",))

        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (ru_st, "run_on_system_startup",))

        self.conn.commit()

    # проверка, что программа запускается первый раз
    def check_first_time_run(self) -> int:
        self.cursor.execute("SELECT PARAM from settings WHERE NAME = ?",
                            ("first_time_run",))
        state = self.cursor.fetchall()[0][0]
        self.cursor.execute("UPDATE settings SET PARAM = ? WHERE NAME = ?",
                            (0, "first_time_run",))
        self.conn.commit()
        return state

    # запись настроения
    def happy_write(self,
                    date_: Union[str, date],
                    happy_number: int,
                    comment: str) -> None:

        if self.get_today(date_):
            show_mesage(msg="Вы уже записали свое настроение")

        else:
            self.cursor.execute("INSERT INTO happy_calendar (data, happy, comments) VALUES (?, ?, ?)",
                                (date_, happy_number, comment))
            self.conn.commit()

            show_mesage(msg=f"Молодец, все записали)")

    # запись задачи
    def write_task(self,
                   title: str,
                   description: str,
                   deadline_date: str,
                   deadline_state: bool,
                   today_date: str,
                   task_id=None) -> None:
        if not task_id:
            self.cursor.execute(
                str("INSERT INTO task_list "
                    "(deadline, deadlineEnable, name, date_create, description) VALUES (?, ?, ?, ?, ?)"),
                (deadline_date, deadline_state, title, today_date, description))

            self.conn.commit()
            show_mesage(msg="Задача созданна, обязательно напопомним, если дедлайн не сегодня ^_^")

        else:
            self.cursor.execute(
                str("UPDATE task_list "
                    "SET deadline = ?, deadlineEnable = ?, name = ?, date_create = ?, description = ? WHERE id = ?"),
                (deadline_date, deadline_state, title, today_date, description, task_id))

            self.conn.commit()
            show_mesage(msg="Задача изменена, обязательно напопомним, если дедлайн не сегодня ^_^")

    # получение записей настроения определенного дня или всех дней
    def get_today(self,
                  date_: Union[str, date] = None,
                  all_days: bool = False) -> list:
        if all_days:
            self.cursor.execute("SELECT * from happy_calendar")
            days_with_data = self.cursor.fetchall()

            return days_with_data
        elif not all_days and date_:
            self.cursor.execute("SELECT * from happy_calendar WHERE data = ?",
                                (date_,))
            day_with_data = self.cursor.fetchall()

            return day_with_data

    # получение данных задачи или получение всех неуведомленных задач
    def get_tasks(self,
                  task_id: int = None,
                  notif: bool = False) -> list:
        if not task_id:
            if not notif:
                self.cursor.execute("SELECT * from task_list")
                task_list = self.cursor.fetchall()

                return task_list
            else:
                self.cursor.execute("SELECT * from task_list WHERE notified = 0 and deadlineEnable = 1")
                task_list = self.cursor.fetchall()

                return task_list
        else:
            self.cursor.execute("SELECT * from task_list WHERE id = ?", (task_id,))
            task_info = self.cursor.fetchall()[0]

            return task_info

    # удаление задачи
    def del_task(self, t_id) -> None:
        self.cursor.execute(
            "DELETE FROM task_list WHERE id = ?",
            (t_id,))
        self.conn.commit()

        show_mesage(msg="Задача удалена, возвращайтесь еще )")

    # установка статуса уведомлено
    def notif_task(self, tid: id) -> None:
        self.cursor.execute("UPDATE task_list SET notified = 1 WHERE id = ?", (tid,))
        self.conn.commit()
