import streamlit as st
import json
import gspread

st.title("🛠 Режим диагностики")

try:
    # Шаг 1: Проверка наличия секрета
    if "google_json" not in st.secrets:
        st.error("❌ Секрет 'google_json' не найден в настройках (Manage app -> Settings -> Secrets).")
        st.stop()
    st.success("✅ Секрет 'google_json' найден в настройках Streamlit!")

    # Шаг 2: Проверка формата JSON
    try:
        raw_text = st.secrets["google_json"]
        creds_dict = json.loads(raw_text)
        st.success("✅ Текст успешно расшифрован как структура JSON!")
    except json.JSONDecodeError as e:
        st.error(f"❌ Ошибка: Streamlit не смог прочитать JSON. Проверьте лишние кавычки. ({e})")
        st.stop()

    # Шаг 3: Проверка ключа
    if "private_key" not in creds_dict:
        st.error("❌ Внутри JSON не найдено поле 'private_key'.")
        st.stop()
        
    pk = creds_dict["private_key"]
    if "\\n" in pk:
        st.warning("⚠️ Найдены двойные слеши переноса (\\\\n). Исправляем на правильные...")
        creds_dict["private_key"] = pk.replace("\\n", "\n")
        st.success("✅ Переносы строк успешно заменены!")
    elif "\n" not in pk:
        st.error("❌ Ключ сломан: в нём вообще нет переносов строк (сплошной текст).")
        st.stop()
    else:
        st.success("✅ Формат ключа правильный!")

    # Шаг 4: Попытка авторизации
    try:
        st.info("⏳ Пытаемся постучаться в Google...")
        client = gspread.service_account_from_dict(creds_dict)
        st.success("✅ Ключ подошел! Успешная авторизация в Google!")
        
        # Шаг 5: Поиск таблицы
        sheet = client.open("Rental_Base")
        st.success("🎉 ПОБЕДА! Таблица 'Rental_Base' найдена и открыта!")
        st.balloons()
    except Exception as e:
        st.error(f"❌ Ошибка соединения с Google: {e}")

except Exception as e:
    st.error(f"❌ Непредвиденная ошибка скрипта: {e}")