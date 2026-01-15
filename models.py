from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# ==================================================
# データベースのインスタンス生成
# ==================================================
db = SQLAlchemy()


# ==================================================
# ユーザマスタ（店舗情報）
# ==================================================
class User(UserMixin, db.Model):
    __tablename__ = "user_table"

    # DBのID
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # ログインID
    login_id = db.Column(db.String(100), nullable=False, unique=True)
    # パスワード
    password = db.Column(db.String(10), nullable=False)
    # 店舗名
    store_name = db.Column(db.String(100), nullable=False)
    # 店舗URL（クーポンページ）
    store_url = db.Column(db.String, nullable=False)
    # 権限の有無
    master = db.Column(db.Boolean, default=False, nullable=True)

    # 【追加】リレーション定義
    # backref='store_user' により、CouponHistory側から .store_user でUser情報にアクセスできます
    histories = db.relationship("CouponHistory", backref="store_user", lazy=True)


# ==================================================
# クーポン利用歴
# ==================================================
class CouponHistory(db.Model):
    __tablename__ = "coupon_history_table"

    # PK
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 【変更】店舗名そのものではなく、店舗のID（user_table.id）を保存します
    user_id = db.Column(db.Integer, db.ForeignKey("user_table.id"), nullable=False)

    # 利用した日時
    timestamp = db.Column(db.DateTime, default=datetime.now, nullable=False)
