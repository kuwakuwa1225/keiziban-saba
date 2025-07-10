from flask import Flask, request, redirect, url_for, session, render_template
import requests
from datetime import datetime
 
app = Flask(__name__)
app.secret_key = "your-secret-key"  # ←セキュアな値にしてください（例：os.urandom(24).hex()）
 
# LINEチャネル情報（あなたの設定に合わせて）
CHANNEL_ID = "2007643838"
CHANNEL_SECRET = "7bdea19f8f4a816cdd5e19c7bb6dbbbe"
REDIRECT_URI = "https%3A%2F%2Fkeiziban-saba.onrender.com/callback"


 
 
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "エラー：認証コードがありません", 400
 
    try:
        # トークン取得
        token_url = "https://api.line.me/oauth2/v2.1/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CHANNEL_ID,
            "client_secret": CHANNEL_SECRET
        }
 
        token_res = requests.post(token_url, headers=headers, data=data)
        if token_res.status_code != 200:
            return f"[ERROR] トークン取得失敗: {token_res.text}", 500
 
        token_json = token_res.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return f"[ERROR] アクセストークンが空です: {token_json}", 500
 
        # プロフィール取得
        profile_url = "https://api.line.me/v2/profile"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        profile_res = requests.get(profile_url, headers=headers)
        if profile_res.status_code != 200:
            return f"[ERROR] プロフィール取得失敗: {profile_res.text}", 500
 
        profile = profile_res.json()
        user_name = profile.get("displayName", "未取得ユーザー")
 
        # セッションに保存
        session["user_name"] = user_name


     @app.route("/mypage")
def mypage():
    if "user_name" not in session:
        return redirect(url_for("index"))  # 未ログインならトップページへ
    return f"こんにちは、{session['user_name']}さん！ここはあなた専用のページです。"

 
        return redirect(url_for("index"))
 
    except Exception as e:
        return f"[ERROR] 処理中に例外が発生しました: {str(e)}", 500
