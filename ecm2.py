'''
00. import

'''
from streamlit_option_menu import option_menu

import streamlit as st
import pandas as pd
import OpenDartReader
import warnings
import dart_fss
import time, datetime
import re
import os

warnings.filterwarnings('ignore')


## 01. functions
def get_data(dart, code, year = 2022, quarter = "사업보고서"):
    select_cols = ['corp_cls', 'corp_code', 'corp_name', 'inv_prm', 'frst_acqs_de', 'invstmnt_purps', 'frst_acqs_amount', 'trmend_blce_qy', 'trmend_blce_qota_rt', 'trmend_blce_acntbk_amount']
    change_cols = ['법인구분', '고유번호', '회사명', '법인명', '최초취득일자', '출자목적', '최초취득금액', '기말잔액수량', '기말잔액지분율', '기말잔액장부가액']
    change_cls = {"Y":"유가", "K":"코스닥", "N":"코넥스", "E":"기타"}
    
    change_dict = {"1분기보고서": 11013, "반기보고서": 11012, "3분기보고서": 11014, "사업보고서":11011}
    r_code = change_dict[quarter]
    
    invst_df = dart.report(code, '타법인출자', year, r_code)
    
    if invst_df.shape[0] == 0:
        return invst_df
    else:
        invst_df = invst_df.loc[:, select_cols]
        invst_df.corp_cls = invst_df.corp_cls.map(change_cls)
        invst_df.columns = change_cols
        return invst_df

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('CP949')    

def main():
    p_bar = st.progress(0.0, text=progress_text)

    ## SOURCE CODE
    api_key = '1b39652cef07f626c9d37375edf582ee51b1407f'
    dart = OpenDartReader(api_key)
    dart_fss.set_api_key(api_key=api_key)

    corp_dict = dart_fss.api.filings.get_corp_code()
    corp_df = pd.DataFrame(corp_dict)
    corp_df = corp_df.loc[corp_df.stock_code.notnull()]
    corp_df.index = [x for x in range(corp_df.shape[0])]

    pass_list = []
    t_cnt = 0
    cnt = 0
    p_ratio = 0.0
    sleep_opt = 0.1

    for code in corp_df.corp_code.unique():
        try:
            temp_df = get_data(dart, code, year, r_code)

            if temp_df.shape[0] == 0:
                pass_list.append(code)
                time.sleep(sleep_opt)
                cnt += 1
                p_ratio = cnt / corp_df.shape[0]
                p_bar.progress(p_ratio, text=progress_text)
                continue

            elif (temp_df.shape[0] != 0) & (t_cnt == 0):
                output_df = temp_df
            else:
                output_df = output_df.append(temp_df)

            cnt += 1
            t_cnt += 1
            time.sleep(sleep_opt)

        except:
            time.sleep(3)
            temp_df = get_data(dart, code, year, r_code)

            if temp_df.shape[0] == 0:
                pass_list.append(code)
                time.sleep(sleep_opt)
                cnt += 1
                p_ratio = cnt / corp_df.shape[0]
                p_bar.progress(p_ratio, text=progress_text)
                continue

            elif (temp_df.shape[0] != 0) & (t_cnt == 0):
                output_df = temp_df
            else:
                output_df = output_df.append(temp_df)

            cnt += 1
            t_cnt += 1
            p_ratio = cnt / corp_df.shape[0]
            p_bar.progress(p_ratio, text=progress_text)
            time.sleep(sleep_opt)

    p_ratio = 1.0
    p_bar.progress(p_ratio, text=progress_text)
    save_df = output_df.loc[(output_df['출자목적'] == '단순투자') & (output_df['법인명'].isin(list(corp_df.corp_name.unique())))]
    save_df.index = [x for x in range(save_df.shape[0])]
    st.dataframe(save_df)

    save_df = convert_df(save_df)
    st.download_button(label="Download", data=save_df, file_name='ECM_타법인출자-단순투자-{}-{}.csv'.format(year, r_code), mime='text/csv')

## 02. path
data_path = os.getcwd() + "\\datasets\\"
if not os.path.isdir(data_path):
    os.mkdir(data_path)
    
## 03. layout
st.set_page_config(layout='wide')
progress_text = "Operation in progress. Please wait."
change_dict = {"1분기보고서": 11013, "반기보고서": 11012, "3분기보고서": 11014, "사업보고서": 11011}

# 화면
with st.sidebar:
    selected = option_menu("Menu", ["타법인출자현황"],
                           icons=['card-list'],
                           menu_icon='cast', default_index=0)

## 메인 틀 작성
st.header('ECM2부 - 타법인출자현황(단순투자)')

with st.form(key='form1'):
    c1, c2 = st.columns(2)
    with c1:
        year = st.selectbox('연도',[x for x in range(2015, datetime.datetime.now().year+1)])
    with c2:
        r_code = st.radio("보고서 선택", ("1분기보고서", "반기보고서", "3분기보고서", "사업보고서"), horizontal=True)
    form1_bt = st.form_submit_button('조회')
    
if st.session_state.get('button') != True:
    st.session_state['button'] = form1_bt

if st.session_state.get('button') == True:
    # 파일 존재할 경우
    if os.path.isfile(data_path + "ECM_타법인출자-단순투자-{}-{}.csv".format(year, r_code)):
        st.warning("""ECM_타법인출자-단순투자-{}-{} 파일이 저장소에 존재합니다. 재수집하시겠습니까?
        \n (아니오 선택 시 기존 파일을 불러옵니다.)""".format(year,r_code), icon="⚠️")

        inside_c1, inside_c2 = st.columns(2)

        with inside_c1:
            btn1 = st.button('예')
        with inside_c2:
            btn2 = st.button('아니오')

        if btn1:
            main()

        elif btn2:
            save_df = pd.read_csv(data_path + 'ECM_타법인출자-단순투자-{}-{}.csv'.format(year, r_code))
            st.dataframe(save_df)
            save_df = convert_df(save_df)
            st.download_button(label="Download", data=save_df, file_name='ECM_타법인출자-단순투자-{}-{}.csv'.format(year, r_code), mime='text/csv')

    else:
        main()