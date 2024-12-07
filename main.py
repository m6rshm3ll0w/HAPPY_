import datetime
import os
import sys

from PyQt6 import uic
from PyQt6.QtCore import QCoreApplication, Qt, QTimer, QDate
from PyQt6.QtGui import QIcon, QAction, QPixmap
from PyQt6.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QMessageBox, QVBoxLayout, QLabel, \
    QPushButton, QFrame, QHBoxLayout, QFileDialog

from MODULES.BD.init import DB_connection
from MODULES.MESSAGE_CREATOR import show_mesage
from MODULES.OTHER.init_all import init_all, VERSION, By
from MODULES.STATISTICS.CSV_EXPORT import csv_export
from MODULES.STATISTICS.graph import render_graph


class Hello(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('DATA/ui/hello.ui', self)  # загрузка UI
        self.initUI()

    def initUI(self):
        self.version_label.setText(f"{VERSION} & {By}")  # подставление переменных в приветственное окно
        self.closeButton.clicked.connect(lambda: self.hide())  # привязка нажатия
        self.setWindowTitle("Привет!!!")  # установка заголовка
        self.setWindowIcon(QIcon('DATA/icon.png'))  # и иконки

        # загрузка изображения
        pixmap = QPixmap('./DATA/icon.png')
        self.limage.setPixmap(pixmap)
        self.limage.setScaledContents(True)

    # отключение закрытия окна
    def closeEvent(self, event):
        event.ignore()
        self.hide()


# Функции для запуска окон с параметрами

# показ графика
def graph_show():
    days: list = db.get_today(all_days=True)  # получение всех дней из бд

    # инициализация переменных для построения графика
    dates: list = []
    moods: list = []
    comments: list = []

    # Парсинг данных из кортежа в списки
    for day in days:
        dates.append(day[0])
        moods.append(day[1])
        comments.append(day[2])

    # Запуск показа графика --> MODULES.STATISTICS.graph
    render_graph(dates, moods, comments)


# пере-инициализация окна записи настроения
def happy_show():
    global happy_window  # задание глобали, для изменения ее значения

    # пересоздание класса окна
    happy_window.destroy()  # уничтожение
    happy_window = Write_happy()  # инициализация

    happy_window.show()  # показ окна


# запуск окна записи задачи с возможностью изменения задачи
def task_show(task_id=None):
    global task_creator_window  # задание глобали, для изменения ее значения

    # пересоздание класса окна
    task_creator_window.destroy()
    task_creator_window = Task_create()

    # проверка передаваемого аргумента
    if not task_id:
        task_creator_window.show()  # если нет, то отображаем обычное окно
    else:
        task_data = db.get_tasks(task_id=task_id)
        task_creator_window.edit_task(task_data)  # иначе передаем в форму данные изменяемой задачи
        task_creator_window.show()  # показ окна


# показ окна настроек и его обновление
def settings_show():
    global settings_window  # задание глобали, для изменения ее значения

    # пересоздание класса окна
    settings_window.destroy()
    settings_window = Settings()

    settings_window.show()


# показ окна задач
def task_mgr_show():
    global task_mgr_window  # задание глобали, для изменения ее значения

    # пересоздание класса окна
    task_mgr_window.destroy()
    task_mgr_window = Task_manager()

    task_mgr_window.show()


### ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑
### ОСНОВНЫЕ КЛАССЫ ПРИЛОЖЕНИЯ      ↓↓↓↓↓↓↓↓↓↓↓↓↓↓


# Иконка в трее
class Tray_icon(QWidget):
    def __init__(self):
        # базовая инициализация
        super().__init__()
        self.tray_icon_set()

    def tray_icon_set(self):
        # создание иконки и установка изображения
        self.tray_icon_obj = QSystemTrayIcon(self)
        self.tray_icon_obj.setIcon(QIcon("./DATA/icon.png"))

        # создание меню трея
        menu = QMenu()

        # добавление кнопок и их привязка
        add_happy = QAction("Записать настроение", self)
        add_happy.triggered.connect(lambda: happy_show())
        menu.addAction(add_happy)

        stats = QAction("Статистика настроения", self)
        stats.triggered.connect(lambda: graph_show())
        menu.addAction(stats)

        settings = QAction("Открыть настройки", self)
        settings.triggered.connect(lambda: settings_show())
        menu.addAction(settings)

        add_task = QAction("Добавить задачу", self)
        add_task.triggered.connect(lambda: task_show())
        menu.addAction(add_task)

        show_welcome = QAction("Приветственное окно", self)
        show_welcome.triggered.connect(lambda: welcome_window.show())
        menu.addAction(show_welcome)

        show_calendar = QAction("Просмотр Задач", self)
        show_calendar.triggered.connect(lambda: task_mgr_show())
        menu.addAction(show_calendar)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(lambda: self.app_quit())
        menu.addAction(exit_action)

        # установка menu как контекстного меню для иконки, а также ее показ
        self.tray_icon_obj.setContextMenu(menu)
        self.tray_icon_obj.show()

    def app_quit(self):
        # создание окон подтверждения выхода
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Подтверждение")
        dlg.setText("Вы точно хотите выйти из приложения?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)  # настройка кнопок
        dlg.setIcon(QMessageBox.Icon.Question)  # выбор типа уведомления
        dlg.setWindowIcon(QIcon("./DATA/icon.png"))  # иконка
        button = dlg.exec()  # запуск

        if button == QMessageBox.StandardButton.Yes:
            QCoreApplication.quit()
            os.system("TASKKILL /F /IM python.exe /T")  # для полного и мгновенного завершения приложения

        else:
            # окно об отмене выхода
            dlg1 = QMessageBox(self)
            dlg1.setWindowTitle("Инфо")
            dlg1.setText("Выход отменен!")
            dlg1.setStandardButtons(QMessageBox.StandardButton.Ok)  # настройка кнопок
            dlg1.setIcon(QMessageBox.Icon.Information)  # выбор типа уведомления
            dlg1.setWindowIcon(QIcon("./DATA/icon.png"))
            dlg1.exec()  # запуск

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# Окно со списком всех задач
class Task_manager(QWidget):
    def __init__(self):
        # базовая инициализация
        super().__init__()
        self.initUI()

        # запуск дополнтельных функций
        self.load_tasks()

    def initUI(self):
        uic.loadUi('DATA/ui/task_manage.ui', self)  # загрузка ui
        self.setWindowTitle("Просмотр Задач")
        self.setWindowIcon(QIcon('./DATA/icon.png'))

        self.updateButton.clicked.connect(lambda: self.load_tasks())  # привязка кнопки

    def load_tasks(self):
        # автоматический парсинг задач из бд в scroll-widget
        task_list = db.get_tasks()  # получение всех задач

        self.widget = QWidget()  # виджет в который добавляется лайоут, для загрузки в scroll-widget
        self.vbox = QVBoxLayout()  # создание лайоута в который добавляется описание задачи

        # установка максимальной ширины окна для красивого отображения
        a = self.size().width() - 30
        self.widget.setMinimumWidth(a)
        self.widget.setMaximumWidth(a)

        # парсинг задач в виджет
        for task in task_list:
            # задание названия и темы
            date_of_create, name = QLabel(f"Созданно: {task[4]}"), QLabel(f"Тема: {task[3]}")

            # проверка наличия описания
            if not task[5] or task[5] == "":
                description = QLabel(f"Описание: отсутствует")
            else:
                description = QLabel(f"Описание: {task[5]}")

            # проверка наличия дедлайн'а
            if task[2] == 1:
                deadline = QLabel(f"Дедлайн: {task[1]}")
            else:
                deadline = QLabel(f"Дедлайн: нет")

            # настройка кнопок
            buttons = QHBoxLayout()  # использование горизонтального расположения

            b1, b2 = QPushButton("Изменить"), QPushButton("Выполнено")

            # подключения кнопок
            b1.clicked.connect(lambda _, task_id=task[0]: task_show(task_id=task_id))
            b2.clicked.connect(lambda _, task_id=task[0]: self.done_task_delete(task_id))

            buttons.addWidget(b1)
            buttons.addWidget(b2)

            # разделительная линия
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            line.setLineWidth(2)

            # добавление основной информации
            self.vbox.addWidget(date_of_create)
            self.vbox.addWidget(name)
            self.vbox.addWidget(description)
            self.vbox.addWidget(deadline)
            self.vbox.addLayout(buttons)
            self.vbox.addWidget(line)

        # после парсинга в QVBoxLayout добавляем его в виджет для scroll-widget
        self.widget.setLayout(self.vbox)

        # отключение горизонтальной прокрутки
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # отключение изменения размера виджета и устанавливаем в качестве внутреннего элемента self.widget
        self.scroll.setWidgetResizable(False)
        self.scroll.setWidget(self.widget)

    def done_task_delete(self, task_id):
        # удаление задачи при нажатии на кнопку выполнено
        dlg = QMessageBox(self)  # всплывающее окно
        dlg.setWindowTitle("Подтверждение")
        dlg.setText("Вы точно хотите удалить эту задачу?")
        dlg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        dlg.setIcon(QMessageBox.Icon.Question)
        button = dlg.exec()  # запуск

        if button == QMessageBox.StandardButton.Yes:
            db.del_task(task_id)  # если нажато да, то удаление задачи
            self.load_tasks()  # перезагрузка списка задач
        else:
            pass

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# форма для создания задачи
class Task_create(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('DATA/ui/task_create.ui', self)  # загрузка ui
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('./DATA/icon.png'))
        self.setWindowTitle("Создание Задачи")

        # установка минимального дедлайн'а на текущую дату и отключение отоброжения вреемени
        self.deadline_data.setMinimumDate(QDate.currentDate())
        self.deadline_data.setDisplayFormat("yyyy.MM.dd")

        # привязка изменения состояния чекбокса
        self.deadlineEnable.setCheckState(Qt.CheckState.Checked)
        self.deadlineEnable.stateChanged.connect(lambda: self.set_deadline())

        # настройка кнопки закрыть и добавить
        self.closeButton.clicked.connect(lambda: self.hide())
        self.create.clicked.connect(lambda: self.write2db())

    def set_deadline(self):
        # в зависимости от состояния чекбокса отключение/включение виджета Qdate
        if self.deadlineEnable.isChecked() is True:
            self.deadline_data.setEnabled(True)
        else:
            self.deadline_data.setEnabled(False)

    def write2db(self, task_id=None, today_date=None):
        # запись в бд
        # получение значения полей и даты дедлайна
        title = self.task_name.text()
        # проверка наличия названия, иначе не создастся задача
        if title == "":
            show_mesage(msg="пожалуйста, укажите название")  # функция из модуля: MODULES.MESSAGE_CREATOR
            return 0  # остановка выполнения функции

        # остальные поля
        description = self.comment.toPlainText()
        deadline_state = self.deadlineEnable.isChecked()
        deadline_date = self.deadline_data.date()
        deadline_date = f"{deadline_date.year()}-{deadline_date.month()}-{deadline_date.day()}"

        # если не указан номер задачи, то создается новая, иначе изменятся
        if not task_id:
            today = datetime.date.today().strftime('%Y-%m-%d')
            db.write_task(title, description, deadline_date, deadline_state, today)  # запись в бд

            task_mgr_window.load_tasks()  # перезагрузка списка задач в классе Task_manager


        else:
            today = today_date  # указание даты создания задачи в качестве текущей даты, для правильного отображения
            # запись в бд с указанием task_id
            db.write_task(title, description, deadline_date, deadline_state, today, task_id)

            task_mgr_window.load_tasks()  # перезагрузка списка задач в классе Task_manager

        QTimer().singleShot(1000, lambda: self.hide())  # автоматическое скрытие окна через 1 секунду после записи в бд

    def edit_task(self, data):
        # загрузка данных изменяемой задачи
        task = data[0]
        deadline: str = data[1]
        deadlineEnabled = data[2]
        title = data[3]
        creation_data = data[4]
        description = data[5]

        # установка значения чекбокса
        if deadlineEnabled == 1:
            self.deadlineEnable.setCheckState(Qt.CheckState.Checked)
        else:
            self.deadlineEnable.setCheckState(Qt.CheckState.Unchecked)

        # установка названия и комментария к задаче
        self.comment.setPlainText(description)
        self.task_name.setText(title)

        self.create.setText('Обновить')  # вместо текста добавить на кнопке пишем обновить

        # установка дедлайн'а
        self.deadline_data.setDate(QDate.fromString(deadline, "yyyy-MM-dd"))
        self.create.clicked.disconnect()
        self.create.clicked.connect(lambda: self.write2db(task_id=task, today_date=creation_data))

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# окно настроек
class Settings(QWidget):
    def __init__(self):
        super().__init__()

        self.time2 = None
        self.time1 = None

        uic.loadUi('DATA/ui/settings.ui', self)
        self.initUI()

        # загрузка значений из бд и включение/выключение изменения времени в зависимости от состояния чекбокса
        self.load_from_db()
        self.edit_params()

    def initUI(self):
        self.setWindowIcon(QIcon('./DATA/icon.png'))
        self.setWindowTitle("Настройки")

        # минимальное значение и шаг горизонтального селектора для уведомлений о не заполненном настроении
        self.time_selector.setMinimum(15)
        self.time_selector.setSingleStep(2)

        # минимальное, максимальное значение и шаг горизонтального селектора для задач
        self.time_selector_2.setMinimum(1)
        self.time_selector_2.setSingleStep(1)
        self.time_selector_2.setMaximum(7)

        # при изменении значения, изменяем текст подписи
        self.time_selector.valueChanged.connect(self.update_slider1)
        self.time_selector_2.valueChanged.connect(self.update_slider2)

        # настройка кнопок и чекбокс'ов
        self.close_conf.clicked.connect(lambda: self.hide())
        self.apply_conf.clicked.connect(lambda: self.write2db())
        self.enable_message.stateChanged.connect(lambda: self.edit_params())
        self.dont_compleated_task.stateChanged.connect(lambda: self.edit_params())

        self.export2csv.clicked.connect(lambda: self.export())

    def export(self):
        # экспорт таблицы настроения в csv файл
        try:
            # запуск окна выбора пути сохранения
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV Files (*.csv);;All Files (*)")
            csv_export(file_path)

            # уведомление о том что файл успешно сохранен
            dlg = QMessageBox(self)
            dlg.setWindowTitle("ОК")
            dlg.setText("Файл Сохранен!!!")
            dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
            dlg.setIcon(QMessageBox.Icon.Information)
            dlg.setWindowIcon(QIcon("./DATA/icon.png"))
            dlg.show()  # запуск

        except Exception as E:
            print(E)

    def load_from_db(self):
        # получение параметров из базы данных
        msg_enable, msg_timeout, msg_deadline_timeout, msg_tasks, ru_st = db.db_get_settings()

        # настройка чекбоксов
        if msg_enable == 1:
            self.enable_message.setCheckState(Qt.CheckState.Checked)
        else:
            self.enable_message.setCheckState(Qt.CheckState.Unchecked)

        if msg_tasks == 1:
            self.dont_compleated_task.setCheckState(Qt.CheckState.Checked)
        else:
            self.dont_compleated_task.setCheckState(Qt.CheckState.Unchecked)

        # загрузка значений слайдеров
        self.time_selector.setValue(msg_timeout if isinstance(msg_timeout, int) else 15)
        self.time_selector_2.setValue(msg_deadline_timeout if isinstance(msg_deadline_timeout, int) else 1)

    def edit_params(self):
        # включение или отключение слайдеров исходя из состояния соответствующего чекбокса
        if not self.enable_message.isChecked():
            self.time_selector.setEnabled(False)
        else:
            self.time_selector.setEnabled(True)

        if not self.dont_compleated_task.isChecked():
            self.time_selector_2.setEnabled(False)
        else:
            self.time_selector_2.setEnabled(True)

    def write2db(self):
        # запись в базу данных
        # получение значений полей
        msg_enable = self.enable_message.isChecked()
        msg_timout = self.time1
        msg_deadline_timeout = self.time2
        msg_tasks = self.dont_compleated_task.isChecked()

        # запись в бд соответственно
        db.settings_write(msg_enable, msg_timout, msg_deadline_timeout, msg_tasks, 1)
        show_mesage(msg="Параметры приложения были применены")

    def update_slider1(self, value):
        # обновление подписей для слайдера времени
        self.time1 = value
        self.show_time.setText(f"{value}")

    def update_slider2(self, value):
        # обновление подписей для слайдера с кол-вом дней
        self.time2 = value
        self.days_show.setText(f"{value} день(дней) до дедлайна")

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# окно для заполнения настроения
class Write_happy(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('DATA/ui/write_happy.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Запись Настроения")
        self.setWindowIcon(QIcon('./DATA/icon.png'))

        # настройка кнопок
        self.write_happy.clicked.connect(lambda: self.write2db())
        self.closeButton.clicked.connect(lambda: self.hide())

    def write2db(self):
        # получение выбранного настроения
        if self.one.isChecked():
            happy = 1
        elif self.two.isChecked():
            happy = 2
        elif self.three.isChecked():
            happy = 3
        elif self.four.isChecked():
            happy = 4
        elif self.five.isChecked():
            happy = 5
        elif self.six.isChecked():
            happy = 6
        elif self.seven.isChecked():
            happy = 7
        elif self.eight.isChecked():
            happy = 8
        elif self.nine.isChecked():
            happy = 9
        elif self.ten.isChecked():
            happy = 10
        else:
            # если не выбранно настроение, то функция закончит выполнение
            show_mesage(msg="выбери настроение")
            return 0

        # получение текущей даты
        date_now = datetime.date.today()
        comment_happy = self.comment.toPlainText()

        try:
            # запись в бд
            db.happy_write(date_now, happy, comment_happy)
        except Exception as E:
            print(E)

        QTimer().singleShot(1000, lambda: self.hide())  # автозакрытие окна

    def closeEvent(self, event):
        event.ignore()
        self.hide()


# Импортировать уведомления о не выполненных задачах
if __name__ == '__main__':
    init_all()  # инициализация глобальных переменных и запуск задач уведомления  MODULES.OTHER.init_all
    app = QApplication(sys.argv)

    db = DB_connection()  # класс бд

    welcome_window = Hello()
    settings_window = Settings()
    task_creator_window = Task_create()
    task_mgr_window = Task_manager()
    happy_window = Write_happy()
    tray_widget = Tray_icon()

    # если первый запуск приложения, то показываем приветственное окно
    if db.check_first_time_run() == 1:
        welcome_window.show()
    else:
        show_mesage(msg="приложение запущено в фоновом режиме")

    sys.exit(app.exec())  # запуск приложения
