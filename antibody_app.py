import streamlit as st
import pandas as pd

# 定数設定
ROWS = 8
COLS = 12
POSITIONS = [f"{chr(65+i)}{j+1}" for i in range(ROWS) for j in range(COLS)]

# セッションに保存された抗体情報を初期化
if "rack" not in st.session_state:
    st.session_state.rack = {pos: {"name": "", "clone": "", "fluor": ""} for pos in POSITIONS}

st.title("🧪 抗体ラック管理アプリ（Streamlit版）")

# 検索バー
search = st.text_input("🔍 抗体名・クローン・蛍光色素で検索", "")

# ラック表示
for i in range(ROWS):
    cols = st.columns(COLS)
    for j in range(COLS):
        pos = f"{chr(65+i)}{j+1}"
        ab = st.session_state.rack[pos]
        label = ab['name'] if ab['name'] else pos
        highlight = search.lower() in f"{ab['name']} {ab['clone']} {ab['fluor']}".lower()
        if cols[j].button(label, key=pos, use_container_width=True):
            st.session_state.selected = pos
        if highlight:
            cols[j].markdown("<div style='height:5px;background-color:lime;'></div>", unsafe_allow_html=True)

# 詳細入力フォーム
if "selected" in st.session_state:
    pos = st.session_state.selected
    ab = st.session_state.rack[pos]
    st.subheader(f"位置: {pos}")
    ab["name"] = st.text_input("抗体名", ab["name"])
    ab["clone"] = st.text_input("クローン", ab["clone"])
    ab["fluor"] = st.text_input("蛍光色素", ab["fluor"])
    if st.button("保存"):
        st.session_state.rack[pos] = ab
        del st.session_state.selected
        st.success("保存しました")

# データ出力（CSV）
if st.button("💾 全抗体情報をCSVダウンロード"):
    df = pd.DataFrame.from_dict(st.session_state.rack, orient="index")
    st.download_button(
        label="Download CSV",
        data=df.to_csv().encode("utf-8"),
        file_name="antibody_rack.csv",
        mime="text/csv"
    )
