import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import openpyxl
import graphviz
import matplotlib.font_manager as fm
from matplotlib import rc
import pickle
import warnings
from pathlib import Path
import os

# 폰트 관련 세팅
font_name = fm.FontProperties(fname='./malgun.ttf').get_name()
rc('font', family=font_name)

# API 관련 세팅
warnings.filterwarnings(action='ignore')
API_KEY = 'd7d1be298b9cac1558eab570011f2bb40e2a6825'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Accept-Encoding': '*', 'Connection': 'keep-alive'}
st.set_page_config(layout='wide')

# 화면
with st.sidebar:
    selected = option_menu("Menu", ["주식연계채권", "기업지배구조"],
                           icons=['card-list', 'diagram-3'],
                           menu_icon='cast', default_index=0)

def convert_df(df):
    return df.to_csv().encode('utf-8-sig')

def get_data(knd, corp_nm, start_dt, end_dt, intr_ex_range, intr_sf_range):
    with open('./Mezzanine_new.pkl', 'rb') as f:
        df = pickle.load(f)
        df = df[df['종류'].isin(knd)]
        df['표면이자율(%)'] = df['표면이자율(%)'].str.strip()
        df['만기이자율(%)'] = df['만기이자율(%)'].str.strip()
        df.loc[df['표면이자율(%)'] == '-', '표면이자율(%)'] = -1000
        df.loc[df['만기이자율(%)'] == '-', '만기이자율(%)'] = -1000
        df = df[(df['표면이자율(%)'].astype(float) >= intr_ex_range[0]) & (df['표면이자율(%)'].astype(float) <= intr_ex_range[1])
                & (df['만기이자율(%)'].astype(float) >= intr_sf_range[0]) & (df['만기이자율(%)'].astype(float) <= intr_sf_range[1])]
        if corp_nm == '':
            df = df[(df['공시일'] >= start_dt.strftime('%Y%m%d')) & (df['공시일'] <= end_dt.strftime('%Y%m%d'))]
        else:
            df['발행사'] = df['발행사'].str.replace('주식회사', '').str.replace('(주)', '').str.replace('(', '').str.replace(')',
                                                                                                                  '').str.strip()
            df = df[(df['공시일'] >= start_dt.strftime('%Y%m%d')) & (df['공시일'] <= end_dt.strftime('%Y%m%d'))
                    & (df['발행사'] == corp_nm)]
        df.loc[df['표면이자율(%)'] == -1000, '표면이자율(%)'] = '-'
        df.loc[df['만기이자율(%)'] == -1000, '만기이자율(%)'] = '-'
        df = df.reset_index(drop=True)
    return df


if selected == "주식연계채권":

    st.header('주식연계채권 발행내역')
    with st.form(key='form1', clear_on_submit=True):
        knd = st.multiselect('> 채권 종류', ('전환사채권', '신주인수권부사채권', '교환사채권'))
        c1, c2, c3 = st.columns(3)
        with c1:
            corp_nm = st.text_input('> 발행사명(전체 기업 검색 시 공란)', '삼성전자')
        with c2:
            start_dt = st.date_input('> 시작일')
        with c3:
            end_dt = st.date_input('> 종료일', min_value=start_dt)
        c4, c5 = st.columns(2)
        with c4:
            intr_ex_range = st.slider('> 표면이자율(%)', 0, 50, (0, 10))
        with c5:
            intr_sf_range = st.slider('> 만기이자율(%)', 0, 50, (0, 10))

        form1_bt = st.form_submit_button('조회')

    if form1_bt:
        df = get_data(knd, corp_nm, start_dt, end_dt, intr_ex_range, intr_sf_range)
        # 총 조회 건수
        row_cnt = "총 " + str(df.shape[0]) + "건"
        st.text(row_cnt)
        st.dataframe(df)

        csv = convert_df(df)

        st.download_button(
                label="Download",
            data=csv,
            file_name='mezzanine.csv',
            mime='text/csv'
        )
    st.markdown(
        """
        <style>
        input{
            font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)

else:
    st.header("기업 지배구조")
    uploaded_file = st.file_uploader("지배구조 데이터를 업로드 해주세요(확장자:xlsx)", type='xlsx', key="file")

    if uploaded_file is not None:

        df = pd.read_excel(uploaded_file)
        # st.dataframe(df)

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
            # print(row['모회사'], row['자회사'])
            f.edge(row['모회사'], row['자회사'], label=row['지분'])

        st.subheader('[지배구조]')
        st.graphviz_chart(f)
