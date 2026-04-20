import streamlit as st
import pandas as pd
import gspread
import json

def connect_to_sheet():
    # 1. Читаем наш JSON из секретов
    creds_dict = json.loads(st.secrets["google_json"])
    
    # 2. ЖЕЛЕЗОБЕТОННАЯ чистка ключа (превращаем текстовые \n в реальные переносы строк)
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    # 3. Используем современный встроенный метод gspread (он умнее и проще)
    client = gspread.service_account_from_dict(creds_dict)
    
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
            st.info("В таблице 'Rental_Base' нет данных. Проверьте заголовки: Модель, Статус, Цена")

        with st.sidebar:
            st.header("➕ Добавить запись")
            model = st.text_input("Название модели")
            status = st.selectbox("Текущий статус", ["Свободен", "В аренде", "В ремонте"])
            price = st.number_input("Стоимость аренды (сутки)", min_value=0, value=500)
            
            if st.button("Отправить в Google Таблицу"):
                if model:
                    transport_sheet.append_row([model, status, price])
                    st.success("Готово! Данные отправлены в облако.")
                    st.rerun()
                else:
                    st.warning("Пожалуйста, введите название!")

    with tab_stock:
        st.subheader("Склад запчастей")
        st.info("Чтобы здесь появились данные, создайте второй лист в вашей Google Таблице.")

except Exception as e:
    st.error(f"Ошибка: {e}")