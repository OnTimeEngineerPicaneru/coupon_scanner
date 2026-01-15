from flask_login import login_user, logout_user, login_required, current_user
from flask import request, redirect, url_for, render_template, jsonify
from sqlalchemy import or_
from models import User, CouponHistory, db
from app import app
import json


# ログイン(管理側用)
@app.route("/master_login", methods=["GET", "POST"])
def master_login():
    if request.method == "POST":
        login_id = request.form.get("login_id")
        password = request.form.get("password")

        user_data = User.query.filter_by(login_id=login_id).first()

        if (user_data is not None) and (password == user_data.password):
            login_user(user_data)

            # 権限チェック
            if current_user.master:
                return redirect(url_for("master_home"))

    # ログインページへ
    return render_template("master_login.html")


# ログアウト(管理者)
@app.route("/logout_master", methods=["GET"])
@login_required
def logout_master():
    if request.method == "GET":
        logout_user()
        return redirect(url_for("master_login"))


# ログアウト(ユーザー側)
@app.route("/logout_coupon", methods=["GET"])
@login_required
def logout_coupon():
    if request.method == "GET":
        logout_user()
        return redirect(url_for("login_coupon"))


# 管理者トップ
@app.route("/master_home")
@login_required
def master_home():
    # 権限チェック
    if current_user.master:
        return render_template("master_home.html")
    else:
        return redirect(url_for("login_coupon"))


# 店舗一覧ページ
@app.route("/store_list")
@login_required
def store_list():
    # 権限チェック
    if current_user.master:
        pass
    else:
        return redirect(url_for("login_coupon"))

    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)
    query = User.query  # queryを作成
    per_page = 50  # 1ページあたりの店舗数

    if keyword:
        # LIKE検索（部分一致） %キーワード% の形にする
        like_word = f"%{keyword}%"
        query = User.query.filter(
            or_(
                User.store_name.ilike(like_word),  # 店舗名
                User.login_id.ilike(like_word),  # ログインID
            )
        )

    # 並び替え
    query = query.order_by(User.id.desc())
    # ページネーション実行
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    stores = pagination.items

    if stores.count == 0:
        pagination = query.paginate(page=page - 1, per_page=per_page, error_out=False)
        stores = pagination.items

    return render_template(
        "master_store_list.html",
        stores=stores,
        pagination=pagination,
        keyword=keyword,
    )


# 店舗詳細ページ
@app.route("/store_detail", methods=["GET", "POST"])
@login_required
def store_detail():
    # 権限チェック
    if current_user.master:
        pass
    else:
        return redirect(url_for("login_coupon"))

    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)
    store = User.query.filter_by(id=request.args.get("id", 1, type=int)).first()

    if request.method == "GET":
        return render_template(
            "master_store_detail.html",
            store=store,
            keyword=keyword,
            page=page,
        )
    else:
        store.store_name = request.form.get("store_name")
        store.login_id = request.form.get("login_id")
        store.password = request.form.get("password")
        store.store_url = request.form.get("store_url")

        db.session.commit()
        return redirect(url_for("store_list", page=page, keyword=keyword))


# 店舗情報の削除
@app.route("/store_delete", methods=["POST"])
@login_required
def store_delete():
    # 権限チェック
    if current_user.master:
        pass
    else:
        return redirect(url_for("login_coupon"))

    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)
    store = User.query.filter_by(id=request.args.get("id", 1, type=int)).first()
    db.session.delete(store)
    db.session.commit()
    return redirect(url_for("store_list", page=page, keyword=keyword))


# 店舗の追加
@app.route("/store_add", methods=["GET", "POST"])
@login_required
def store_add():
    # 権限チェック
    if current_user.master:
        pass
    else:
        return redirect(url_for("login_coupon"))

    if request.method == "GET":
        return render_template("master_store_add.html")
    else:
        new_store_data = User(
            store_name=request.form.get("store_name"),
            login_id=request.form.get("login_id"),
            password=request.form.get("password"),
            store_url=request.form.get("store_url"),
        )
        db.session.add(new_store_data)
        db.session.commit()
        return redirect(url_for("store_list"))


# クーポン利用データ一覧


# ログイン(ユーザー側)
@app.route("/login_coupon", methods=["GET", "POST"])
@login_required
def login_coupon():
    if request.method == "POST":
        login_id = request.form.get("login_id")
        password = request.form.get("password")

        user_data = User.query.filter_by(login_id=login_id).first()

        if (user_data is not None) and (password == user_data.password):
            login_user(user_data)
            return redirect(url_for("scan_coupon"))

    # ログインページへ
    return render_template("store_login.html")


# QRコード読みとり
@app.route("/scan_coupon", methods=["GET", "POST"])
@login_required
def scan_coupon():
    # ----------------------------
    # GET：読取画面を表示
    # ----------------------------
    if request.method == "GET":
        return render_template("store_home.html")

    # ----------------------------
    # POST：ブラウザからQR文字列を受け取る
    # ----------------------------
    # JS(fetch) から JSON で来る想定
    if not request.is_json:
        return jsonify({"ok": False, "message": "JSON形式で送信してください"}), 400

    data = request.get_json(silent=True) or {}
    qr_text = (data.get("qr_text") or "").strip()

    check_text = "xmmFjUhTeU53DWmxNVC2bs4J-VinQMLujw8sSJ6air9C6Rkn3AjxmmieE7n46HrNdiA4Se4M3_eYKbM-3UVErbGyniDn48UCUd9kRh9ME_t8Pu78YeTEwXcP87Qj53SbsaUiFBm-WR36SjfywmjCETYnjHAkEx-GgPdLt6srB7CtAyi5_2E7dRuXgnZMijgPRubM4gPn-AbpgVT7Tt4_CwaDnN5zkmT8wLaRsZX2KjznzUJK5Y2FAG6R3Z"
    if check_text == qr_text:
        # 必要なら、qr_text の内容で追加の判定もできます
        history = CouponHistory(user_id=current_user.id)
        db.session.add(history)
        db.session.commit()
    else:
        return jsonify({"ok": False, "message": "クーポンが利用できません"}), 400

    return (
        jsonify(
            {
                "ok": True,
                "message": "クーポンを承認しました。",
            }
        ),
        200,
    )
