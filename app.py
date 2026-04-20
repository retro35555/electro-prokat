import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json # Добавили библиотеку для чтения сырого JSON

def connect_to_sheet():
    # Читаем текст из Secrets и сразу превращаем в рабочий словарь ключей
    creds_dict = json.loads(st.secrets["google_json"])
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Rental_Base")

st.set_page_config(page_title="Прокат: Облачная база", layout="wide")
st.title("🚲 Управление прокатом и складом")

try:
    google_file = connect_to_sheet()
    transport_sheet = google_file.get_worksheet(0) 
    transport_data = transport_sheet.get_all_records()
    df_transport = pd.DataFrame(transport_data)

    tab_rent, tab_stock = st.tabs(["📋 Аренда транспорта", "🔧 Склад запчастей"])

    with tab_rent:
        st.subheader("Текущий парк транспорта")
        if not df_transport.empty:
            st.dataframe(df_transport, use_container_width=True)
        else:
            st.info("В таблице 'Rental_Base' нет данных. Проверьте первую строку: Модель, Статус, Цена")

        with st.sidebar:
            st.header("➕ Добавить запись")
            model = st.text_input("Название модели")
            status = st.selectbox("Текущий статус", ["Свободен", "В аренде", "В ремонте"])
            price = st.number_input("Стоимость аренды (сутки)", min_value=0, value=500)
            
            if st.button("Отправить в Google Таблицу"):
                if model:
                    transport_sheet.append_row([model, status, price])
                    st.success("Готово! Данные в облаке.")
                    st.rerun()
                else:
                    st.warning("Пожалуйста, введите название!")

    with tab_stock:
        st.subheader("Склад запчастей")
        st.info("Чтобы здесь появились данные, создайте второй лист в вашей Google Таблице.")

except Exception as e:
    st.error(f"Ошибка: {e}")