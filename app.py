from flask import Flask, request, redirect, url_for, session, render_template
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key"

CHANNEL_ID = "2007643838"
CHANNEL_SECRET = "7bdea19f8f4a816cdd5e19c7bb6dbbbe"
REDIRECT_URI = "https://keiziban-saba.onrender.com/callback"

@app.route("/login")
def login():
    auth_url = (
        "https://access.line.me/oauth2/v2.1/authorize"
        "?response_type=code"
        f"&client_id={CHANNEL_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&state=xyz123"
        "&scope=profile%20openid"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "エラー：認証コードがありません", 400

    token_res = requests.post(
        "https://api.line.me/oauth2/v2.1/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CHANNEL_ID,
            "client_secret": CHANNEL_SECRET
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token_json = token_res.json()
    access_token = token_json.get("access_token")
    if not access_token:
        return "アクセストークン取得失敗", 400

    profile_res = requests.get(
        "https://api.line.me/v2/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    profile = profile_res.json()

    # セッションに保存
    session["user_id"] = profile.get("userId")
    session["display_name"] = profile.get("displayName")

    return redirect("/mypage")

@app.route("/mypage")
def mypage():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("mypage.html", line_user_id=session["user_id"])
