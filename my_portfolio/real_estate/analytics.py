import os
import uuid
import base64
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from rpy2.robjects import r, pandas2ri, numpy2ri, default_converter
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr


def run_analysis(df):
    '''
     dfを受け取り、AI予測と統計解析を辞書で返す
    '''
    # HTMLに渡す初期値セット
    result = {
        'top_bargains': [],
        'reliability_msg': "データが不足しています",
        'is_significant': False,
        'plot_data': None,
        'avg_rent': 0,
        'corr_rent_age': 0,
        'ages_list': [],
        'rents_list': [],
        'hist_counts':[],
        'hist_labels':[],
    }

    # データが空なら初期値を返す
    if df.empty:
        return result

    # 1. 基本的な統計の計算（平均値・相関係数）
    result['avg_rent'] = round(df['rent'].mean(), 1)
    corr = df['rent'].corr(df['age'])
    # 相関係数のNan対策
    result['corr_rent_age'] = 0 if pd.isna(corr) else round(corr, 3)
    result['ages_list'] = df['age'].tolist()
    result['rents_list'] = df['rent'].tolist()

    # データ件数が少ない場合AIとRの処理スキップ
    if len(df) <= 5:
        return result

    # 2. Scikit-learnによるAI予測（割安物件抽出）
    X = df[['age', 'distance', 'layout']]
    y = df['rent']
    sk_model = LinearRegression()
    sk_model.fit(X, y)
    df['predicted_rent'] = sk_model.predict(X)
    df['bargain_score'] = df['predicted_rent'] - df['rent']
    result['top_bargains'] = df.sort_values(by='bargain_score', ascending=False).head(5).to_dict('records')

    # 3. rpy2によるRの統計解析とグラフ生成
    try:
            with localconverter(default_converter + pandas2ri.converter + numpy2ri.converter):
                # PythonのdfをRのr_dfに
                stats = importr('stats')
                r.assign("r_df", df)

                # 特定の変数のP値を取り出す
                age_p_value = r('summary(stats::lm(rent ~ age + distance + layout, data=r_df))$coefficients[2, 4]')[0]

                # 判定結果をContextへ
                result['is_significant'] = age_p_value < 0.05 # 5%有意
                p_value_rounded = round(float(age_p_value), 4)

                if result['is_significant']:
                    result['reliability_msg'] = f"この分析結果は統計的に有意です（p = {p_value_rounded}）"
                else:
                    result['reliability_msg'] = f"データ不足のため統計的な有意差は確認できません（p = {p_value_rounded}）"
        
                # 一時保存して表示するためのユニークファイル名
                temp_filename = f"temp_plot_{uuid.uuid4().hex}.png"
                r.assign("temp_filename", temp_filename)

                # ggplot2でグラフを描きファイル保存
                r('''
                library(ggplot2)
                
                # 築年数と家賃の散布図+回帰直線
                p <- ggplot(r_df, aes(x=age, y=rent)) +
                geom_point(alpha=0.5, color="blue") +
                geom_smooth(method="lm", color="red") +
                labs(title="築年数と家賃の関係（AI回帰分析）", x="築年数（年）", y="家賃（万円）") +
                theme_minimal()

                # 画像として保存
                ggsave(temp_filename, plot=p, width=6, height=4, dpi=100)
                ''')

                # 上記をPythonで読み込みBase64に変換
                with open(temp_filename, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    # HTMLに渡せるよう整理
                    result['plot_data'] = f"data:image/png;base64,{encoded_string}"

                # 一時ファイル削除
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        
    except Exception as e:
        reliability_msg = f"Rの解析中にエラーが発生しました:{e}"

    '''
    ヒストグラムデータ収集
    '''
    # 1. 家賃のリスト取得
    rents = df['rent']
    max_rent = int(rents.max()) # .0などの見栄え対策
    
    # 2. 箱（Bin）の境界設定,ラベル設定
    hist_bins = np.arange(0, max_rent + 2, 2)

    #  3. NumPyで集計
    counts, bins = np.histogram(rents, bins=hist_bins)

    # 4. ラベル作成
    labels = [f"{bins[i]}~{bins[i+1]}万円" for i in range(len(bins) -1)]

    # 4. JavaScriptに渡すためリスト型に
    result['hist_counts'] = counts.tolist()
    result['hist_labels'] = labels

    # 計算結果を返却
    return result