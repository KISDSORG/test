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
import time, datetime
import os
import ecm2

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
    selected = option_menu("Menu", ["주식연계채권", "타법인출자현황", "기업지배구조"],
                           icons=['card-list', 'card-list', 'diagram-3'],
                           menu_icon='cast', default_index=0)

def convert_df(df):
    return df.to_csv().encode('utf-8-sig')

def get_data(knd, corp_nm, start_dt, end_dt, intr_ex_min, intr_ex_max, intr_sf_min, intr_sf_max):
    with open('./Mezzanine_new.pkl', 'rb') as f:
        df = pickle.load(f)
        df = df[df['종류'].isin(knd)]
        df['표면이자율(%)'] = df['표면이자율(%)'].str.strip()
        df['만기이자율(%)'] = df['만기이자율(%)'].str.strip()
        df.loc[df['표면이자율(%)'] == '-', '표면이자율(%)'] = -1000
        df.loc[df['만기이자율(%)'] == '-', '만기이자율(%)'] = -1000
        df = df[(((df['표면이자율(%)'].astype(float) >= intr_ex_min) & (df['표면이자율(%)'].astype(float) <= intr_ex_max))|(df['표면이자율(%)'].astype(float)==-1000))
                & (((df['만기이자율(%)'].astype(float) >= intr_sf_min) & (df['만기이자율(%)'].astype(float) <= intr_sf_max))|(df['만기이자율(%)'].astype(float)==-1000))]
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
    with st.form(key='form1'):
        knd = st.multiselect('채권 종류', ('전환사채권', '신주인수권부사채권', '교환사채권'))
        c1, c2, c3 = st.columns(3)
        with c1:
            corp_nm = st.text_input('발행사명(전체 기업 검색 시 공란)')
        with c2:
            start_dt = st.date_input('시작일')
        with c3:
            end_dt = st.date_input('종료일') #, min_value=start_dt)
        c4, c5 = st.columns(2)
        with c4:
            intr_ex_min = st.number_input('표면이자율(%) MIN', min_value=0, max_value=100, value=0)
        with c5:
            intr_ex_max = st.number_input('표면이자율(%) MAX', min_value=0, max_value=100, value=10)
        c6, c7 = st.columns(2)
        with c6:
            intr_sf_min = st.number_input('만기이자율(%) MIN', min_value=0, max_value=100, value=0)
        with c7:
            intr_sf_max = st.number_input('만기이자율(%) MAX', min_value=0, max_value=100, value=10)

        form1_bt = st.form_submit_button('조회')

    if form1_bt:
        df = get_data(knd, corp_nm, start_dt, end_dt, intr_ex_min, intr_ex_max, intr_sf_min, intr_sf_max)
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

elif selected == "타법인출자현황":

    data_path = os.getcwd() + "\\datasets\\"
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    st.header('ECM2부 - 타법인출자현황(단순투자)')

    with st.form(key='form1'):
        c1, c2 = st.columns(2)
        with c1:
            year = st.selectbox('연도', [x for x in range(2015, datetime.datetime.now().year + 1)])
        with c2:
            r_code = st.radio("보고서 선택", ("1분기보고서", "반기보고서", "3분기보고서", "사업보고서"), horizontal=True)
        form1_bt = st.form_submit_button('조회')

    if st.session_state.get('button') != True:
        st.session_state['button'] = form1_bt

    if st.session_state.get('button') == True:
        # 파일 존재할 경우
        if os.path.isfile(data_path + "ECM_타법인출자-단순투자-{}-{}.csv".format(year, r_code)):
            st.warning("""ECM_타법인출자-단순투자-{}-{} 파일이 저장소에 존재합니다. 재수집하시겠습니까?
            \n (아니오 선택 시 기존 파일을 불러옵니다.)""".format(year, r_code), icon="⚠️")

            inside_c1, inside_c2 = st.columns(2)

            with inside_c1:
                btn1 = st.button('예')
            with inside_c2:
                btn2 = st.button('아니오')

            if btn1:
                ecm2.main()

            elif btn2:
                save_df = pd.read_csv(data_path + 'ECM_타법인출자-단순투자-{}-{}.csv'.format(year, r_code))
                st.dataframe(save_df)
                save_df = convert_df(save_df)
                st.download_button(label="Download", data=save_df,
                                   file_name='ECM_타법인출자-단순투자-{}-{}.csv'.format(year, r_code), mime='text/csv')

        else:
            ecm2.main()

else:
    st.header("기업 지배구조")
    uploaded_file = st.file_uploader("지배구조 데이터를 업로드 해주세요(확장자:xlsx)", type='xlsx', key="file")
    # 샘플 파일 다운로드
    with open('./sample.xlsx', 'rb') as f:
        st.download_button('Sample Input File Download', f, file_name='sample.xlsx')

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

        g = graphviz.Digraph('round-table', comment='The Round Table')
        for c in corp:
            g.node(c, c)

        for idx, row in df_pivot.iterrows():
            g.edge(row['모회사'], row['자회사'], label=row['지분'])

        st.graphviz_chart(g)