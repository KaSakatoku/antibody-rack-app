import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials

# スプレッドシートID（あなたが提供してくれたもの）
SPREADSHEET_ID = "15npt2LL-UJeWVxigJ_dHR8LRKrbJfJGieRPo1e0Ph5o"

# 認証：Secrets から JSON を読み込む
creds = Credentials.from_service_account_info(
    json.loads(st.secrets["GOOGLE_CREDENTIALS"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # 最初のシート

# ラックの定義
ROWS, COLS = 8, 12
POSITIONS = [f"{chr(65 + i)}{j+1}" for i in range(ROWS) for j in range(COLS)]

# データの初期化（Google Sheets から読み込む）
@st.cache_data
def load_data():
    df = pd.DataFrame(sheet.get_all_records())
    rack = {row["RackID"]: {"name": row["Name"], "clone": row["Clone"], "fluor": row["Fluor"]} for _, row in df.iterrows()}
    return rack

# データを Google Sheets に保存
def save_data(rack):
    df = pd.DataFrame([
        {"RackID": pos, "Name": ab["name"], "Clone": ab["clone"], "Fluor": ab["fluor"]}
        for pos, ab in rack.items()
    ])
    sheet.clear()
    sheet.append_rows([df.columns.tolist()] + df.values.tolist())

# セッション初期化
if "rack" not in st.session_state:
    st.session_state.rack = load_data()

st.title("🧪 抗体ラック管理アプリ（Google Sheets対応）")

search = st.text_input("🔍 抗体名・クローン・蛍光色素で検索", "")

for i in range(ROWS):
    cols = st.columns(COLS)
    for j in range(COLS):
        pos = f"{chr(65+i)}{j+1}"
        ab = st.session_state.rack.get(pos, {"name": "", "clone": "", "fluor": ""})
        label = ab["name"] if ab["name"] else pos
        highlight = search.lower() in f"{ab['name']} {ab['clone']} {ab['fluor']}".lower()
        if cols[j].button(label, key=pos, use_container_width=True):
            st.session_state.selected = pos
        if highlight:
            cols[j].markdown("<div style='height:5px;background-color:lime;'></div>", unsafe_allow_html=True)

if "selected" in st.session_state:
    pos = st.session_state.selected
    ab = st.session_state.rack.get(pos, {"name": "", "clone": "", "fluor": ""})
    st.subheader(f"位置: {pos}")
    ab["name"] = st.text_input("抗体名", ab["name"])
    ab["clone"] = st.text_input("クローン", ab["clone"])
    ab["fluor"] = st.text_input("蛍光色素", ab["fluor"])
    if st.button("保存"):
        st.session_state.rack[pos] = ab
        save_data(st.session_state.rack)
        st.success("保存されました")
