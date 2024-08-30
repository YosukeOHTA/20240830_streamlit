import streamlit as st
import pandas as pd
import numpy as np
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('-no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
# driver = webdriver.Chrome(service=Service(), options=chrome_options)
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://tiget.net/users/1207563')
time.sleep(4)

history = np.zeros((0,4))
my_bar = st.progress(0)

for i in range(30 ,97):
    my_bar.progress((i-29)/68, text="Operation in progress. Please wait.")
    if len(driver.find_elements(By.XPATH, f'/html/body/div[2]/div[2]/div/div[4]/div/div[2]/div[2]/div/div[{i}]/div/div[1]/a'))>0:
        driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[4]/div/div[2]/div[2]/div/div[{i}]/div/div[1]/a').click()
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[-1])
        item = np.array([
            driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/article/div/header/h1').text,
            driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/article/div/div[2]/div[1]/div/div[1]/div[1]/div[1]').text,
            driver.current_url,
            driver.find_element(By.XPATH, '/html/body/div[2]/div[4]/article/div/div[2]/div[1]/div/div[1]/div[1]/div[2]//span').text,
        ])
        history = np.vstack((history, item))
        driver.switch_to.window(driver.window_handles[0])
my_bar.empty()
df = pd.DataFrame(history, columns=['題名', '日時', 'url', 'チケット状況', ])

ticketList = ['作曲の喜び', '《指揮科だョ!全員集合》', 'CCC(Chamber music concert by 4 composers)']
df2 = df[df['チケット状況']=='当日支払い']
df2 = df2[~df2['題名'].isin(ticketList)]
st.write('取得可能')
st.write(df2)

df3 = df[df['チケット状況']=='受付前']
st.write('受付前')
st.write(df3)
