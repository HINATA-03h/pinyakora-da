import pandas as pd
import matplotlib.pyplot as plt
import os

# 同じフォルダにあるので、ファイル名だけでOK！
CSV_FILE = "temp_log.csv"

def show_my_graph():
    # ファイルの存在チェック
    if not os.path.exists(CSV_FILE):
        print(f"エラー: '{CSV_FILE}' が見つかりません。")
        print("プログラムと同じフォルダにCSVファイルを置いているか確認してください。")
        return

    try:
        # データの読み込み
        df = pd.read_csv(CSV_FILE)
        
        # グラフ作成
        plt.figure(figsize=(10, 5))
        plt.plot(df['Time'], df['Temperature'], 
                 marker='o', linestyle='-', color='orange', label='Temp')

        # グラフの装飾
        plt.title("Temperature Data from Raspberry Pi")
        plt.xlabel("Time")
        plt.ylabel("Temperature (C)")
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()

        # 表示
        print("グラフを表示します...")
        plt.show()

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    show_my_graph()