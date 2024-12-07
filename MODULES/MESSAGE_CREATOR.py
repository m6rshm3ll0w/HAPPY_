from win10toast import ToastNotifier

toast = ToastNotifier()  # создаем экземпляр класса для уведомления


# вызов уведомления
def show_mesage(title: str = "HaPPy",
                msg: str = "",
                duration: int = 1) -> None:
    try:
        toast.show_toast(
            title=title,
            msg=msg,
            duration=duration,
            icon_path="DATA/icon.ico",
            threaded=True,
        )
    except Exception as E:
        print("")

# пример использования
# show_mesage("Не потеряй комбо", "привет, сегодня ты не заполнил настроение")
