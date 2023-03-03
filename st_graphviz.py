import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import openpyxl
import graphviz
import matplotlib.font_manager as fm
from matplotlib import rc

font_name = fm.FontProperties(fname='./malgun.ttf').get_name()
rc('font', family=font_name)

with st.sidebar:
    selected = option_menu("Menu", ["주식연계채권", "기업지배구조"],
                         icons=['house', 'kanban'],
                         menu_icon='app-indicator', default_index=0)

if selected == "주식연계채권":
    st.write("주식연계채권 페이지")
else:
    uploaded_file = st.file_uploader("Choose a file", type='xlsx', key="file")

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)
        st.dataframe(df)

        df = df.fillna(0)
        df = df.rename(columns={'Unnamed: 0': '모회사'})
        df.set_index('모회사', inplace=True)

        df_pivot = df.reset_index().melt(id_vars='모회사')
        df_pivot = df_pivot[df_pivot['value'] > 0]
        df_pivot.rename(columns={'variable': '자회사', 'value': '지분'}, inplace=True)
        df_pivot = df_pivot.astype({'지분': 'string'})

        # 모회사, 자회사 중복 없이 저장
        corp = []
        for index, row in df_pivot.iterrows():
            corp.append(row[0])
            corp.append(row[1])
        corp = set(corp)

        f = graphviz.Digraph('round-table', comment='The Round Table')
        for c in corp:
            f.node(c, c)

        for idx, row in df_pivot.iterrows():
            print(row['모회사'], row['자회사'])
            f.edge(row['모회사'], row['자회사'], label=row['지분'])

        st.graphviz_chart(f)