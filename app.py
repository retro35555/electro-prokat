import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- НАСТРОЙКА GOOGLE TABLES ---
def connect_to_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    # Пытаемся открыть таблицу
    return client.open("Rental_Base")

st.set_page_config(page_title="Прокат: Облачная база", layout="wide")
st.title("🚲 Управление прокатом и складом")

try:
    # Подключаемся к файлу таблицы
    google_file = connect_to_sheet()
    
    # Лист 1: Транспорт (должен быть первым в Google Таблице)
    transport_sheet = google_file.get_worksheet(0) 
    transport_data = transport_sheet.get_all_records()
    df_transport = pd.DataFrame(transport_data)

    # Создаем вкладки
    tab_rent, tab_stock = st.tabs(["📋 Аренда транспорта", "🔧 Склад запчастей"])

    with tab_rent:
        st.subheader("Текущий парк транспорта")
        if not df_transport.empty:
            st.dataframe(df_transport, use_container_width=True)
        else:
            st.info("В таблице пока пусто.")

        # Форма добавления в боковой панели
        with st.sidebar:
            st.header("➕ Добавить позицию")
            add_type = st.radio("Что добавляем?", ["Транспорт", "Запчасть"])
            
            if add_type == "Транспорт":
                model = st.text_input("Модель")
                status = st.selectbox("Статус", ["Свободен", "В аренде", "В ремонте"])
                price = st.number_input("Цена в сутки", min_value=0, value=500)
                
                if st.button("Сохранить транспорт"):
                    if model:
                        transport_sheet.append_row([model, status, price])
                        st.success("Добавлено!")
                        st.rerun()
                    else:
                        st.error("Введите название!")

    with tab_stock:
        st.subheader("Запчасти в наличии")
        st.info("Для управления складом создайте второй лист в Google Таблице.")
        # Здесь в будущем выведем таблицу со второго листа

except Exception as e:
    st.error(f"Произошла ошибка: {e}")
    st.info("Совет: проверь, что в Google Таблице есть данные и заголовки: Модель, Статус, Цена")