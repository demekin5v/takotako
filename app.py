import os
# ファイル名をチェックする関数
from werkzeug.utils import secure_filename
# 画像のダウンロード
from flask import send_from_directory
# splite3をimportする
import sqlite3
# flaskをimportしてflaskを使えるようにする
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session

# fromでstatistics.pyというモジュール(ファイル)を読み込む、importでstatistics.py内のmean()という関数を読み込む
import statistics
from statistics import mean
import datetime  # datetimeというモジュール(ファイル)を読み込む

# appにFlaskを定義して使えるようにしています。Flask クラスのインスタンスを作って、 app という変数に代入しています。
app = Flask(__name__)

# Flask では標準で Flask.secret_key を設定すると、sessionを使うことができます。この時、Flask では session の内容を署名付きで Cookie に保存します。
app.secret_key = 'takoyaki'

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def regist():
    return render_template('regist.html')
# 必要ならtakoyaki.htmlに治す


# GET  /register => 登録画面を表示
# POST /register => 登録処理をする
@app.route('/takoyaki')
def takoyaki():
    return render_template('/takoyaki.html')


@app.route('/complete')
def complete():
    return render_template('/complete.html')


@app.route('/profile', methods=["GET", "POST"])
def profile():
    #  登録ページを表示させる
    if request.method == "GET":
        return render_template("profile.html")
    # ここからPOSTの処理
    else:
        session['username'] = request.form.get("username")
        session['gu'] = request.form.get("gu")
        session['topping'] = request.form.get("topping")
        session['source'] = request.form.get("source")
        session['resipi'] = request.form.get("resipi")
        py_user = request.form.get("structure_user")
        py_gu = request.form.get("structure_gu")
        py_topping = request.form.get("structure_topping")
        py_source = request.form.get("structure_source")
        py_takoyakiname = request.form.get("structure_takoyakiname")
        # password = request.form.get("password")
# item = { "id":id, "comment":comment }
        # item = {"id": id, "comment": comment, "postdate": postdate}
        # 画像
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            imgdata = '/static/img/' + filename
            session['imgdata'] = filename
            # conn = sqlite3.connect('service.db')
            # c = conn.cursor()
            # c.execute("insert into user values(null,?,?,?)",(name,password,imgdata))
            # conn.commit()
            # conn.close()
            # return redirect('/login')
            conn = sqlite3.connect('service.db')
            c = conn.cursor()
            c.execute("INSERT INTO structure VALUES (null,?,?,?,?,?,?)",
                      (py_user,  py_gu,  py_topping,  py_source,  py_takoyakiname, imgdata))
            conn.commit()
            c.close()
            return redirect('/meishi')
        else:
            return ''' <p>許可されていない拡張子です</p> '''


@app.route('/static/img/<filename>')
def uploaded_file(filename):
    print(session['imgdata'])
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# /add ではPOSTを使ったので /edit ではあえてGETを使う
@app.route("/meishi", methods=["GET"])
def meishi():
    print("fuckyou")
    print(session['imgdata'])
    # ブラウザから送られてきたデータを取得
    py_user = request.form.get("structure_user")
    py_gu = request.form.get("structure_gu")
    py_topping = request.form.get("structure_topping")
    py_source = request.form.get("structure_source")
    py_takoyakiname = request.form.get("structure_takoyakiname")

    if "username" in session:
        user_id_py = session["username"]
    if "gu" in session:
        gu_id_py = session["gu"]
    if "topping" in session:
        topping_id_py = session["topping"]
    if "source" in session:
        source_id_py = session["source"]
    if "resipi" in session:
        resipi_id_py = session["resipi"]
    if "imgdata" in session:
        file_id_py = session["imgdata"]
        print(file_id_py)

        conn = sqlite3.connect('service.db')
        c = conn.cursor()
        c.execute("SELECT id FROM structure WHERE user = ? AND gu = ?",
                  (py_user, py_gu))
        user_id = c.fetchone()
        c.close()
    else:
        print("<p>許可されていない拡張子です</p>")

    return render_template("meishi.html", username=user_id_py, gu=gu_id_py, topping=topping_id_py, source=source_id_py, resipi=resipi_id_py, img_file=file_id_py)


# @app.route('/regist')
# def regist_get():
#     return render_template('regist.html')


@app.route('/regist', methods=["POST"])
def regist_post():
    py_name = request.form.get("member_name")
    py_password = request.form.get("member_password")
    conn = sqlite3.connect('service.db')
    c = conn.cursor()
    c.execute("INSERT INTO member VALUES (null,?,?)", (py_name, py_password))
    conn.commit()
    c.close()
    return render_template('/complete.html')


@app.route('/login')
def login_get():
    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_post():
    py_name = request.form.get('member_name')
    py_password = request.form.get('member_password')
    conn = sqlite3.connect('service.db')
    c = conn.cursor()
    c.execute("SELECT id FROM member WHERE name = ? AND password = ?",
              (py_name, py_password))
    user_id = c.fetchone()
    c.close()
    if user_id is None:
        return render_template('/login.html')
    else:
        return redirect("/meishi")


@ app.errorhandler(403)
def mistake403(code):
    return 'There is a mistake in your url!'


@ app.errorhandler(404)
def notfound404(code):
    return "404だよ！！見つからないよ！！！"


# __name__ というのは、自動的に定義される変数で、現在のファイル(モジュール)名が入ります。 ファイルをスクリプトとして直接実行した場合、 __name__ は __main__ になります。
if __name__ == "__main__":
    # Flask が持っている開発用サーバーを、実行します。
    app.run(debug=True)
