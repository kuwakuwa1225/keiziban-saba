from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime

app = Flask(name)

授業リスト
classes = ["プログラミング演習", "情報工学実践", "データ解析"]

授業ごとの投稿データを保存（メモリ上）
class_posts = {name: [] for name in classes}

@app.route("/")
def index():
    return render_template("index.html", classes=classes)

@app.route("/class/<class_name>", methods=["GET", "POST"])
def class_board(class_name):
    if class_name not in classes:
        return "授業が見つかりません", 404

    if request.method == "POST":
        content = request.form.get("content")
        if content:
            class_posts[class_name].append({
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return redirect(url_for("class_board", class_name=class_name))

    return render_template("board.html", class_name=class_name, posts=class_posts[class_name])

if name == "main":
    app.run(debug=True)
