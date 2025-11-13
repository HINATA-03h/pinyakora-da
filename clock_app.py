###必要なライブラリのインポート
import streamlit as st
###日時取得のためのライブラリ
import datetime
###自動更新のためのライブラリ
from streamlit_autorefresh import st_autorefresh
###データをテキスト形式に変換するコード
import base64
###音声再生のためのpygame
import pygame
###HTML埋め込みのためのライブラリ
import webbrowser
import requests
import json
###HTML埋め込みのためのライブラリ
import streamlit.components.v1 as components

tabs = st.tabs(["時計", "目覚まし時計", "カウントダウンタイマー", "おみくじ", "天気予報"])

with tabs[0]:
###背景画像をBase64で埋め込む関数
    def get_base64_of_image(image_file):
         with open(image_file, "rb") as f:
            data = f.read()
         return base64.b64encode(data).decode()

###時間　条件分岐
    now = datetime.datetime.now()
    hour = now.hour
    if 4 < hour < 7:
        bg_image = bg_image = get_base64_of_image("morning.jpg")
    elif 7<= hour < 16:
         bg_image = get_base64_of_image("noon.jpg")
    elif 16<= hour <19:
        bg_image = get_base64_of_image("evening.jpg")
    else:
        bg_image = get_base64_of_image("night.jpg")

###背景画像の設定
    st.markdown(
       f"""
       <style>
       html, body {{
        height: 100%;
        margin: 0;
        overflow: hidden;  
        }}
        .stApp {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-color: rgba(0,0,0,0.3);
        background-blend-mode: multiply;
        }}
        </style>
        """,
        unsafe_allow_html=True
        )

###タイトルを中央に
    st.markdown( """ 
    <h1 style='text-align: center; color: red; font-size: 80px;'> 
    ⏰時計⏰ 
    </h1> """,
     unsafe_allow_html=True 
    )

###自動更新（1秒ごと）
    st_autorefresh(interval=1000, key="clockapp")

###現在の日時表示
    now = datetime.datetime.now()
    current_time = now.strftime("%m月%d日 %H:%M:%S")

###時計を中央に配置
    st.markdown(
        f"""
        <style>
        .center-box {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 30vh;
        margin: 0;
        overflow: hidden;
        }}
        .clock-text {{
        font-size: 80px;
        color: black;
        background: rgba(255, 255, 255, 0.5);
        padding: 20px 30px;
        border-radius: 20px;
        }}
        </style>
        <div class="center-box">
        <div class="clock-text">{current_time}</div>
        </div>
        """,
        unsafe_allow_html=True
        )


###目覚まし時計
with tabs[1]:
    st.markdown("""<h1 style = 'text-align:center; color:yellow; font-size:80px'>目覚まし時計</h1>""", unsafe_allow_html=True)
    
###pygameをリセット
    if "pygame_init" not in st.session_state:
         st.session_state.pygame_init = True
         pygame.mixer.quit()
         pygame.mixer.init()
         pygame.mixer.music.load("alarm.mp3")
         st.session_state.alarm_set = False
         st.session_state.alarm_triggered = False  

###session_stateの初期化
    if "alarm_playing" not in st.session_state:
        st.session_state.alarm_playing = False
    if "alarm_stopped_today" not in st.session_state:
        st.session_state.alarm_stopped_today = None
    if "alarm_triggered" not in st.session_state:
        st.session_state.alarm_triggered = False

###アラーム時間設定
    alarm_time = st.time_input("時刻を設定してください",  value=datetime.time(0, 0),  key="alarm_time", step= datetime.timedelta(minutes=1))
    st.write (f"設定された時刻: {alarm_time}")

###現在の日時取得
    now = datetime.datetime.now()
    today = now.date()

###アラーム時間と現在時間が一致したら音を鳴らす
    if (now.hour == alarm_time.hour and now.minute == alarm_time.minute and st.session_state.alarm_stopped_today != today):
        if not st.session_state.alarm_playing and not st.session_state.alarm_triggered:
            pygame.mixer.music.play(-1)  ###ループ再生
            st.session_state.alarm_playing = True
            st.session_state.alarm_triggered = True
            st.markdown(
                """
                <h2 style='text-align: center; color: blue; font-size: 50px;'>
                ⏰おはようございます！⏰
                </h2>
                """,   
                unsafe_allow_html=True
                )  

###ストップボタン
    if st.button("ストップ") and st.session_state.alarm_playing:
        pygame.mixer.music.stop()
        st.session_state.alarm_playing = False
        st.session_state.alarm_triggered = False
        st.session_state.alarm_stopped_today = today 

###カウントダウンタイマーの起動
with tabs[2]:
    components.html(open("countdowntimer", encoding="utf-8").read(), height=600)

###おみくじ
with tabs[3]:
    components.html(open("omikuji.html", encoding="utf-8").read(), height=500)


### 天気予報
with tabs[4]:
    st.markdown(
        """<h1 style='text-align:center; color:skyblue; font-size:60px'>
        天気予報
        </h1>""",
        unsafe_allow_html=True
    )

    city = st.text_input("都市名を入力してください（例：Tokyo）", value="Tokyo")

###初期化
    if "tenki_data" not in st.session_state:
        st.session_state.tenki_data = None
    if "last_city" not in st.session_state:
        st.session_state.last_city = ""

###ボタンが押された or 都市名が変わったときに再取得
    if st.button("天気予報を取得") or city != st.session_state.last_city:
        api_key = "21306745ca5f5fac29dead5864ceb938"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=ja&units=metric"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            st.session_state.tenki_data = {
                "city": city,
                "weather_description": data["weather"][0]["description"],
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
            }
            st.session_state.last_city = city
        else:
            st.error("都市名が正しくありません。もう一度試してください。")

###天気情報の表示
    if st.session_state.tenki_data:
        data = st.session_state.tenki_data
        st.markdown(
            f"""
            <h2 style='text-align:center; color:#0000ff; font-size:40px;
            border:5px solid white; padding:10px; border-radius:10px;
            background-color:rgba(255,255,255,0.5);'>
            {data['city']} Weather Forecast
            </h2>
            <p style='text-align:center; font-size:55px; color:white;'>
            天気: {data['weather_description']}<br>
            気温: {data['temperature']}°C<br>
            湿度: {data['humidity']}%
            </p>
            """,
            unsafe_allow_html=True,
        )
