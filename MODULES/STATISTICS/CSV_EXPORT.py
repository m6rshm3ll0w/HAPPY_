import csv
from MODULES.BD.init import DB_connection


# экспорт в csv
def csv_export(file_path: str) -> None:
    # подключение к бд
    db = DB_connection("./DATA/Dbase.db3")
    days = db.get_today(all_days=True)

    data = []

    # парсинг данных в список в виде словаря
    for day in days:
        data.append({"дата": day[0], "настроение": day[1], "комментарии": day[2]})

    #  запись в csv по заданному пути
    with open(file_path, 'w', newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(data[0].keys()),
            delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        for d in data:
            writer.writerow(d)