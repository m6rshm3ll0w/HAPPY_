import pandas as pd
import plotly.express as px


# показ графика через plotly
def render_graph(date_list: list[str],
                 happy_list: list[int],
                 comments_list: list[str]) -> bool:
    try:
        # создание дата-фрейма
        df = pd.DataFrame(dict(
            дата=date_list,
            настроение=happy_list,
            комментарий=comments_list))

        # загрузка его в plotly.express.line
        fig = px.line(df, x='дата', y='настроение', hover_data="комментарий")
        # показ в браузере
        fig.show()

        return True
    except Exception as E:
        # обработка исключения
        print(E)
