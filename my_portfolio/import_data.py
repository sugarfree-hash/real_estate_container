import os
import django
import json

# 環境設定読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Modelをインポート
from real_estate.models import HousePrice

def main():
    json_file = 'dummy_estate_data.json'
    
    # 1. JSONファイルを読み込む
    # リストに変換
    with open(json_file, 'r')as f:
        data = json.load(f)

    # 2. ループ処理でデータベースに保存する    
    for item in data:
        HousePrice.objects.create(
            id = item['id'],
            rent = item['rent'],
            age = item['age'],
            distance = item['distance'],
            layout = item['layout']
        )

    # -----------------------------------------------------

    print("データの取り込みが完了しました")

if __name__ == '__main__':
    main()