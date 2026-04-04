# 1. ベースとなるOS（軽量なPython入りLinux）
FROM python:3.10-slim

# 2. Linuxのパッケージマネージャーで、JavaとR（+ggplot2）をインストール
RUN apt-get update && apt-get install -y \
    default-jre \
    r-base \
    r-cran-ggplot2 \
    && rm -rf /var/lib/apt/lists/*

# 3. 箱の中の「作業部屋」を /app という名前に設定
WORKDIR /app

# 4. Pythonの持ち物リストをコピーしてインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 5. コードやJARファイルなど、すべてを箱の中にコピー
COPY . /app/

# 6. 箱を起動したときに最初に実行するコマンド（Gunicorn起動）
# --timeout 120 はRの解析時間を考慮した長めの設定
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120"]