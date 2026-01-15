from flask import Flask
from flask_migrate import Migrate
from models import db, User
from flask_login import LoginManager
from markupsafe import Markup
from datetime import datetime
import os


# ===================================================
# インスタンス生成
# ===================================================
app = Flask(__name__)

# ===================================================
# 設定ファイルの読み込み
# ===================================================
app.config.from_object("config.Config")


# ===================================================
# データベース
# ===================================================
db.init_app(app)
migrate = Migrate(app, db)


# ===================================================
# FlaskとLoginの紐づけ
# ===================================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ユーザIDを引数としてそのIDに対するユーザ情報をデータベースから取得する
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===================================================
# メイン処理
# ===================================================
from views import *

if __name__ == "__main__":
    app.run()
