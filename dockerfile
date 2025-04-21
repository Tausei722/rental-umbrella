# ベースイメージとしてPython公式イメージを使用
FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 必要なPythonライブラリをインストールするために、requirements.txtをコピー
COPY requirements.txt .

# ライブラリをインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコンテナにコピー
COPY . .

# コンテナ内で実行するコマンドを指定
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
