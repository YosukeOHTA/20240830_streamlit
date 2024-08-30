import json
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import streamlit as st
import time

f = open('../../userinfo.json', 'r')
json_dict = json.load(f)
libPw = json_dict['library1']['passWord']

with st.form(key='Library check'):
    url1 = "https://opac.lib.city.yokohama.lg.jp/winj/opac/login.do"
    st.header(f'Library check [link]({url1})')
    # text box
    libIdList1 = st.multiselect(
        'Library ID',
        ['9027551499', '9027551502', '9027551510', ],
        ['9027551499', '9027551502', '9027551510', ]
    )

    # button
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')
    if submit_btn:
        progress_bar = st.progress(0)
        history1 = np.zeros((0,4))
        col1 = ['userID', 'byDate', 'bookName', 'author',]
        history2 = np.zeros((0,4))
        col2 = ['userID', 'status', 'bookName', 'author',]

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        for i, libId in enumerate(libIdList1):
            progress_bar.progress((i+1)/len(libIdList1))
            st.write(f'Library ID :{libId} の確認中')
            driver.get('https://opac.lib.city.yokohama.lg.jp/winj/opac/top.do')
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ul/li/a').click()
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/form/dl/dd[1]/input').send_keys(libId)
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/form/dl/dd[2]/input').send_keys(libPw)
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div/form/input').click()
            # Myライブラリ
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/ul/li[7]/a').click()
            # 貸出中の本
            driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/ul/li[1]/a/dl/dt').click()
            if driver.find_element(By.XPATH, '/html/body/div[2]/div[1]').text != '貸出中の本\n該当するリストが存在しません。':
                numBooks1 = int(driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/form/div[6]/p').text.split('全')[1].split('件')[0])
                for i in range(numBooks1):
                    item1 = np.array([
                        libId,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/div/p[2]').text.split(':')[2],
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/h4/span/a/span').text,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/div/p[1]').text.split('--')[0].split('／')[0],
                    ])
                    history1 = np.vstack((history1, item1))
            # Myライブラリ
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/ul/li[7]/a').click()
            time.sleep(1)
            # 予約中の本
            driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/ul/li[2]/a/dl/dt').click()
            if driver.find_element(By.XPATH, '/html/body/div[2]/div[1]').text != '予約中の本\n有効予約一覧\n取消済予約一覧\n該当するリストが存在しません。':
                numBooks2 = int(driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/form/div[5]/p').text.split('全')[1].split('件')[0])
                for i in range(numBooks2):
                    item2 = np.array([
                        libId,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/div/div/p').text.split('(')[-1].split('位')[0],
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/h4/a/span').text,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div[1]/form/ol/li[{str(i+1)}]/div/div[1]/div/p[1]').text.split('--')[0].split('／')[0],
                    ])
                    history2 = np.vstack((history2, item2))

            # ログアウト
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ul[1]/li[2]/a').click()
            # トップメニュー
            driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/a').click()
        driver.close()
        df1 = pd.DataFrame(history1, columns=col1).drop_duplicates()
        df2 = pd.DataFrame(history2, columns=col2)
        for i in df2.index:
            if '回送中' in df2.loc[i, 'status']:
                df2.loc[i, 'status']='0'
            if '受取可' in df2.loc[i, 'status']:
                df2.loc[i, 'status']='0'
        df2['status'] = df2['status'].astype('int')
        st.subheader('借りている本')
        st.dataframe(df1.sort_values(['byDate', 'userID', 'bookName']))
        st.subheader('予約している本')
        st.dataframe(df2.sort_values(['status', 'bookName', ], ascending=True))

with st.form(key='eLibrary check'):
    url2 = "https://web.d-library.jp/yokohama/g0101/top/"
    st.header(f'eLibrary check [link]({url2})')
    # text box
    libIdList2 = st.multiselect(
        'Library ID',
        ['9027551499', '9027551502', '9027551510', ],
        ['9027551499', '9027551502', '9027551510', ]
    )

    # button
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')
    if submit_btn:
        progress_bar = st.progress(0)
        history3 = np.zeros((0,4))
        col3 = ['userID', 'byDate', 'bookName', 'author',]
        history4 = np.zeros((0,3))
        col4 = ['userID', 'status', 'bookName', ]

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")

        driver = webdriver.Chrome(options=chrome_options)
        for i, libId in enumerate(libIdList2):
            progress_bar.progress((i+1)/len(libIdList2))
            st.write(f'Library ID :{libId} の確認中')
            driver.get('https://web.d-library.jp/yokohama/g0101/top/')
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/form/table/tbody/tr[1]/td/input').send_keys(libId)
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/form/table/tbody/tr[2]/td/input[1]').send_keys(libPw)
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/form/table/tbody/tr[3]/td/button').click()
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/div/table/tbody/tr[1]/td/a').click()
            # 貸出中の本
            numRental = int(driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div[1]/div/h2/span/em/span[1]').text)
            if numRental != 0:
                for i in range(numRental):
                    item3 = np.array([
                        libId,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/ul/li[{i+1}]/div/div[2]/div[1]/dl[2]/dd').text,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/ul/li[{i+1}]/div/div[2]/div[1]/a').text,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/ul/li[{i+1}]/div/div[2]/div[1]/dl[1]/dd').text,
                    ])
                    history3 = np.vstack((history3, item3))
            # 予約中の本
            numBook = int(driver.find_element(By.XPATH, '/html/body/div[2]/div/div[2]/div[2]/div[2]/div/h2/span/em/span[1]').text)
            if numBook !=0:
                for i in range(numBook):
                    item4 = np.array([
                        libId,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/ul/li[{i+1}]/div/div[2]/div/dl[2]/dd[2]').text,
                        driver.find_element(By.XPATH, f'/html/body/div[2]/div/div[2]/div[2]/div[2]/div/div/ul/li[{i+1}]/div/div[2]/div/a').text,
                    ])
                    history4 = np.vstack((history4, item4))
            # ログアウト
            driver.find_element(By.XPATH, '/html/body/div[2]/div/div[1]/div[1]/div[1]/table/tbody/tr[2]/td/a').click()
        driver.close()
        df3 = pd.DataFrame(history3, columns=col3).drop_duplicates()
        df4 = pd.DataFrame(history4, columns=col4)
        st.subheader('借りている本')
        st.dataframe(df3.sort_values(['byDate', 'userID', 'bookName']))
        st.subheader('予約している本')
        st.dataframe(df4.sort_values(['status', 'bookName', ], ascending=True))
