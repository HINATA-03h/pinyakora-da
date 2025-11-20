###必要なライブラリのインポート
import streamlit as st
###日時取得のためのライブラリ
import datetime
###タイムゾーン対応のためのライブラリ
import pytz
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


###スマホ対応のためのCSS
st.markdown("""
<style>
@media (max-width: 600px) {
    h1 {
        font-size: 40px !important;
    }
    h2 {
        font-size: 30px !important;
    }
    p {
        font-size: 26px !important;
    }
    .clock-text {
        font-size: 40px !important;
        padding: 10px 15px !important;
    }
    .center-box {
        height: 20vh !important;
    }
}
</style>
""", unsafe_allow_html=True)

tabs = st.tabs(["時計", "目覚まし時計", "カウントダウンタイマー", "おみくじ", "天気予報","電卓"])

with tabs[0]:
###背景画像をBase64で埋め込む関数
    def get_base64_of_image(image_file):
         with open(image_file, "rb") as f:
            data = f.read()
         return base64.b64encode(data).decode()

###時間　条件分岐
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)  

    hour = now.hour
    if 4 < hour < 7:
         bg_image = get_base64_of_image("morning.jpg")
    elif 7 <= hour < 16:
         bg_image = get_base64_of_image("noon.jpg")
    elif 16 <= hour < 19:
        bg_image = get_base64_of_image("evening.jpg")
    else:
        bg_image = get_base64_of_image("night.jpg")

###時計表示部分も修正
    now = datetime.datetime.now(jst)
    current_time = now.strftime("%m月%d日 %H:%M:%S")

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
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)
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


### 目覚まし時計
with tabs[1]:
    st.markdown("""<h1 style='text-align:center; color:yellow; font-size:80px'>
    目覚まし時計
    </h1>""", unsafe_allow_html=True)

###音声をBase64で読み込み
    def load_audio_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    alarm_audio_base64 = load_audio_base64("alarm.mp3")

### セッションステートの初期化 
    if "prepared" not in st.session_state:
        st.session_state.prepared = False
    if "alarm_stopped_today" not in st.session_state:
        st.session_state.alarm_stopped_today = None
    if "alarm_ringing" not in st.session_state:
        st.session_state.alarm_ringing = False

### 音声再生の許可を得る準備ボタン
    st.subheader("🔊 最初に必ず押してください")
    if st.button("🎵 音声を準備する（無音を再生します）"):
        st.session_state.prepared = True

###無音ファイルを再生
        st.markdown(
            """
            <audio autoplay>
                <source src="data:audio/mp3;base64,SUQzAwAAAAA=" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )
        st.success("音声の準備が完了しました！アラームが自動再生できるようになりました。")

###アラーム時刻の入力 
    alarm_time = st.time_input(
        "⏰ アラーム時刻を設定してください",
        value=datetime.time(0, 0),
        key="alarm_time",
        step=datetime.timedelta(minutes=1)
    )
    st.write(f"設定された時刻: {alarm_time}")

###現在時刻 
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.datetime.now(jst)
    today = now.date()

###準備完了 → アラームチェック 
    if st.session_state.prepared:
        alarm_should_ring = (
            now.hour == alarm_time.hour
            and now.minute == alarm_time.minute
            and st.session_state.alarm_stopped_today != today
        )
    else:
        alarm_should_ring = False

###アラーム自動再生 
    if alarm_should_ring:
        st.session_state.alarm_ringing = True

### alarm.mp3 を自動再生
        st.markdown(
            f"""
            <audio autoplay loop>
                <source src="data:audio/mp3;base64,{alarm_audio_base64}" type="audio/mp3">
            </audio>
            <h2 style='text-align:center; color:blue; font-size:50px;'>
            ⏰ おはようございます！ ⏰
            </h2>
            """,
            unsafe_allow_html=True
        )
    else:
        st.session_state.alarm_ringing = False

### 停止ボタン 
    if st.button("⛔ アラームを停止"):
        st.session_state.alarm_stopped_today = today
        st.session_state.alarm_ringing = False

###音声を停止させるための空タグ
        st.markdown(
            """
            <audio autoplay>
                <source src="">
            </audio>
            """,
            unsafe_allow_html=True
        )


###カウントダウンタイマーの起動
with tabs[2]:
    components.html(open("countdowntimer/countdowntimer.html", encoding="utf-8").read(), height=600)

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

###セッションステートの初期化
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
###電卓
with tabs[5]:
    st.markdown("""
    <h1 style='text-align:center; color:orange; font-size:70px'>
    電卓
    </h1>
    """, unsafe_allow_html=True)

###電卓専用CSS（スマホ100%対応）
    st.markdown("""
    <style>
    .calc-container {
        width: 100%;
        max-width: 360px;
        margin: auto;
    }

    .display-box {
        background: #222;
        color: #fff;
        padding: 20px;
        font-size: 8vw;
        border-radius: 10px;
        text-align: right;
        width: 100%;
        margin-bottom: 20px;
        box-sizing: border-box;
    }

    /* スマホ向けボタンデザイン */
    button[kind="secondary"] {
        background-color: #444 !important;
        color: white !important;
        border-radius: 12px !important;
        height: 70px !important;
        font-size: 6vw !important;
    }

    /* Cボタンだけ赤色 */
    .btn-clear button {
        background-color: #ff5555 !important;
        color: white !important;
        font-weight: bold !important;
    }

    @media (min-width: 500px) {
        .display-box {
            font-size: 40px;
        }
        button[kind="secondary"] {
            font-size: 26px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

###セッションステート初期化 
    if "calc_display" not in st.session_state:
        st.session_state.calc_display = ""

    # --- ボタン動作 ---
    def calc_press(key):
        if key == "C":
            st.session_state.calc_display = ""
        elif key == "=":
            try:
                st.session_state.calc_display = str(eval(st.session_state.calc_display))
            except:
                st.session_state.calc_display = "Error"
        else:
            st.session_state.calc_display += key

###表示部分
    st.markdown(
        f"""
        <div class="calc-container">
            <div class="display-box">{st.session_state.calc_display}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

###ボタン配置 
    buttons = [
        ["7", "8", "9", "+"],
        ["4", "5", "6", "-"],
        ["1", "2", "3", "*"],
        ["0", ".", "=", "/"]
    ]

    for row in buttons:
        cols = st.columns(len(row), gap="small")
        for i, key in enumerate(row):
            with cols[i]:
                st.button(
                    key,
                    key=f"btn_{key}",
                    on_click=calc_press,
                    args=(key,),
                    use_container_width=True
                )

###Cボタン
    st.container().markdown("<br>", unsafe_allow_html=True)
    colC = st.columns(1)
    with colC[0]:
        st.button(
            "C",
            key="btn_clear",
            on_click=calc_press,
            args=("C",),
            use_container_width=True,
            type="secondary"
        )
