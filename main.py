import streamlit as st
# import requests
# import zipfile
# import os
# import pandas as pd
# from bs4 import BeautifulSoup
import warnings

warnings.filterwarnings(action='ignore')
API_KEY = 'd7d1be298b9cac1558eab570011f2bb40e2a6825'
headers= {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
          'Accept-Encoding': '*', 'Connection': 'keep-alive'}
st.set_page_config(layout='wide')

# def convert_df(df):
#     return df.to_csv().encode('utf-8-sig')


if __name__ == '__main__':
          
    st.sidebar.title('주식연계채권 발행내역')

    knd = st.sidebar.multiselect(
        '채권 종류', ('전환사채권', '신주인수권부사채권', '교환사채권')
    )
          
    corp_nm = st.sidebar.text_input('발행사명', '삼성전자')
    start_dt = st.sidebar.date_input('시작일')
    end_dt = st.sidebar.date_input('종료일', min_value=start_dt)
    intr_ex = st.sidebar.slider('표면이자율(%)', 0, 10)
    intr_sf = st.sidebar.slider('만기이자율(%)', 0, 10)

    st.write('표면이자율: ', intr_ex, '%')
    st.write('만기이자율: ', intr_sf, '%') 

    if knd == '전환사채권':
        st.write('You selected 전환사채권')
    elif knd == '신주인수권부사채권':
        st.write('You selected 신주인수권부사채권')
    else:
        st.write("You selected 교환사채권")

    # st.title('주식연계채권 발행내역 :money_with_wings:')
    #
    # corp = st.text_input('기업명', '삼성전자')
    # start = st.date_input('시작일')
    # end = st.date_input('종료일', min_value=start)

    # button 생성하기
    # if st.button('조회'):
    #     df = get_corp_code(corp, start, end)
    #     st.dataframe(df)
    #
    #     csv = convert_df(df)
    #
    #     st.download_button(
    #         label="Download",
    #         data=csv,
    #         file_name='st_sample.csv',
    #         mime='text/csv'
    #     )
