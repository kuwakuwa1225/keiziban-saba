from flask import Flask, request, render_template, redirect, url_for, session
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key"  # セッション用（ランダム文字列でOK）

# LINEログイン設定（自分のLINEチャネル情報を入力）
CHANNEL_ID = "2007643838"
CHANNEL_SECRET = "7bdea19f8f4a816cdd5e19c7bb6dbbbe"
REDIRECT_URI = "https://your-app-name.onrender.com/callback"  # RenderのURLに合わせて

# 授業リスト
classes = ["プログラミング演習", "基礎情報数学", "微分積分", "論理設計", "コンピュータ演習", "情報セキュリティ", "線形代数"]
class_posts = {name: [] for name in classes}

@app.route("/")
def index():
    user_name = session.get("user_name")
    return render_template("index.html", classes=classes, user_name=user_name)

@app.route("/class/<class_name>", methods=["GET", "POST"])
def class_board(class_name):
    if class_name not in classes:
        return "授業が見つかりません", 404

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            post_id = len(class_posts[class_name]) + 1
            class_posts[class_name].append({
                "id": post_id,
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "author": session.get("user_name", "匿名")  # 投稿者名を記録
            })
        return redirect(url_for("class_board", class_name=class_name))

    return render_template("board.html", class_name=class_name, posts=class_posts[class_name], user_name=session.get("user_name"))

@app.route("/login")
def login():
    login_url = (
        "https://access.line.me/oauth2/v2.1/authorize"
        "?response_type=code"
        f"&client_id={CHANNEL_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&state=xyz123"
        "&scope=profile%20openid"
    )
    return redirect(login_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "エラー：認証コードがありません", 400

    # アクセストークン取得
    token_url = "https://api.line.me/oauth2/v2.1/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CHANNEL_ID,
        "client_secret": CHANNEL_SECRET
    }

    token_res = requests.post(token_url, headers=headers, data=data)
    token_json = token_res.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return f"トークン取得失敗: {token_json}", 500

    # プロフィール取得
    profile_url = "https://api.line.me/v2/profile"
    headers = { "Authorization": f"Bearer {access_token}" }
    profile_res = requests.get(profile_url, headers=headers)
    profile = profile_res.json()

    session["user_name"] = profile.get("displayName", "未取得ユーザー")
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
