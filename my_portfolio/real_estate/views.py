import json
import subprocess
import pandas as pd
from . import analytics
from django.shortcuts import render
from django.shortcuts import redirect
from .models import HousePrice


def house_list(request):
    # 1. データ取得
    houses = HousePrice.objects.all()

    # 2. 検索フィルタリング
    max_rent = request.GET.get('max_rent')
    max_age = request.GET.get('max_age')

    if max_rent:
        houses = houses.filter(rent__lte=max_rent)

    if max_age:
        houses = houses.filter(age__lte=max_age)

    # 3. Pandasデータフレームへ変換
    df = pd.DataFrame(list(houses.values()))

    # 4. 分析をanalytics.pyへ
    analysis_result = analytics.run_analysis(df)

    # テンプレートへ渡すデータの作成
    context = {
        'houses':houses,
        **analysis_result,
    }

    return render(request, 'real_estate/house_list.html', context)

def generate_new_data(request):
    '''Javaを叩いてDBを更新する関数'''

    jar_path = 'real_estate/data_generator.jar'

    if request.method == 'POST':

        try:
            # Javaの実行
            subprocess.run(
                ['java', '-jar', jar_path],
                check=True,
                capture_output=True,
                text=True
            )

            read_file = 'real_estate/dummy_estate_data.json'
            # JSONファイル読み込み
            with open(read_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)

            # DBの入れ替え
            HousePrice.objects.all().delete()

            # 辞書データをHousePriceモデルにするため新しいリストに
            instances = [
                HousePrice(
                    rent=item['rent'],
                    age=item['age'],
                    distance=item['distance'],
                    layout=item['layout']
                )
                for item in data_list
            ]
            HousePrice.objects.bulk_create(instances)


        except Exception as e:
            print(f"データ更新中にエラーが発生しました: {e}")

    return redirect('house_list')