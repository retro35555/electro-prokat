import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def connect_to_sheet():
    # Получаем данные из секретов
    creds_info = dict(st.secrets["gcp_service_account"])
    
    # Исправляем форматирование ключа, если оно сбилось
    if "private_key" in creds_info:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
    
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_info, scope)
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
            
            # Добавим возможность удалить или изменить данные позже
        else:
            st.info("В таблице пока нет данных. Добавьте первый велосипед!")

        with st.sidebar:
            st.header("➕ Добавить позицию")
            model = st.text_input("Модель")
            status = st.selectbox("Статус", ["Свободен", "В аренде", "В ремонте"])
            price = st.number_input("Цена в сутки", min_value=0, value=500)
            
            if st.button("Сохранить"):
                if model:
                    transport_sheet.append_row([model, status, price])
                    st.success("Добавлено в Google Таблицу!")
                    st.rerun()

    with tab_stock:
        st.subheader("Склад запчастей")
        st.write("Чтобы склад заработал, создай второй лист в таблице 'Rental_Base'.")

except Exception as e:
    st.error(f"Ошибка подключения: {e}")