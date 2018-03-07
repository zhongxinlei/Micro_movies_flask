# coding:utf8

from . import home
from flask import render_template, redirect, url_for, flash, session, request
from app.home.forms import RegistForm, LoginForm, UserdetailForm, PwdForm
import uuid
from app import db, app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app.models import User, Userlog, Preview, Tag, Movie
from functools import wraps
import os
from datetime import datetime
from app.admin.views import change_filename


def user_login_req(f):
    @wraps(f)
    def decrated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("home.login", next=request.url))
        return f(*args, **kwargs)

    return decrated_function


#
# @home.route("/")
# def index():
#     # return "<h1 sytle='color:green'>this is home</h1>"
#     return render_template("home/index.html")

@home.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            if not user.check_pwd(data["pwd"]):
                flash("password is not correct!", "error")
            else:
                session["user"] = user.name
                session["user_id"] = user.id
                userlog = Userlog(
                    user_id=user.id,
                    ip=request.remote_addr,
                )
                db.session.add(userlog)
                db.session.commit()
                return redirect(url_for("home.user"))
        else:
            flash("user dose not exists", "error")
    return render_template("home/login.html", form=form)


@home.route("/logout/")
def logout():
    session.pop("user", None)
    session.pop("user_id", None)
    return redirect(url_for("home.login"))


@home.route("/register/", methods=["GET", "POST"])
def register():
    print('i am in home/register')
    form = RegistForm()
    if form.validate_on_submit():
        data = form.data
        user = User(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            pwd=generate_password_hash(data["pwd"]),
            uuid=uuid.uuid4().hex
        )
        db.session.add(user)
        db.session.commit()
        flash("registration succeded!", "ok")
    return render_template("home/register.html", form=form)


@home.route("/user/", methods=["GET", "POST"])
@user_login_req
def user():
    form = UserdetailForm()
    user = User.query.get(int(session["user_id"]))
    if request.method == "GET":
        form.name.data = user.name
        form.email.data = user.email
        form.phone.data = user.phone
        form.info.data = user.info
    if form.validate_on_submit():
        data = form.data
        file_face = secure_filename(form.face.data.filename)
        if not os.path.exists(app.config["FC_DIR"]):
            os.makedirs(app.config["FC_DIR"])
            os.chmod(app.config["FC_DIR"], 777)
        user.face = change_filename(file_face)
        form.face.data.save(app.config["FC_DIR"] + user.face)
        name_count = User.query.filter_by(name=data["name"]).count()
        if data["name"] != user.name and name_count == 1:
            flash("name already exists!", "error")
            return redirect(url_for("home.user"))
        email_count = User.query.filter_by(email=data["email"]).count()
        if data["email"] != user.email and email_count == 1:
            flash("email already exists!", "error")
            return redirect(url_for("home.user"))
        phone_count = User.query.filter_by(phone=data["phone"]).count()
        if data["phone"] != user.phone and phone_count == 1:
            flash("phone already exists!", "error")
            return redirect(url_for("home.user"))
        user.name = data["name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.info = data["info"]
        db.session.add(user)
        db.session.commit()
        flash("modification succeeded", "ok")
        return redirect(url_for("home.user"))
    return render_template("home/user.html", form=form, user=user)


@home.route("/pwd/", methods=["GET", "POST"])
@user_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        user = User.query.get(int(session["user_id"]))
        if not user.check_pwd(data["old_pwd"]):
            flash("ols password is not correct!", "error")
            return redirect(url_for("home.pwd"))
        user.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(user)
        db.session.commit()
        flash("password modification succeeded!", "ok")
        return redirect(url_for("home.pwd"))
    return render_template("home/pwd.html", form=form)


@home.route("/comments")
@user_login_req
def comments():
    return render_template("home/comments.html")


@home.route("/loginlog/<int:page>/", methods=["GET"])
@user_login_req
def loginlog(page=None):
    if page is None:
        page = 1
    page_data = Userlog.query.filter_by(
        user_id=int(session["user_id"])
    ).order_by(
        Userlog.addtime.desc()
    ).paginate(page=page, per_page=6)
    return render_template("home/loginlog.html", page_data=page_data)


@home.route("/moviecol/")
@user_login_req
def moviecol():
    print("i am at moviecol")
    return render_template("home/moviecol_list.html")


@home.route("/<int:page>/", methods=["GET"])
@home.route("/", methods=["GET"])
def index(page=None):
    tags = Tag.query.all()
    page_data = Movie.query
    tid = request.args.get("tid", 0)
    if int(tid) != 0:
        page_data = page_data.filter_by(tag_id=int(tid))
    star = request.args.get("star", 0)
    if int(star) != 0:
        page_data = page_data.filter_by(star=int(star))
    time = request.args.get("time", 0)
    if int(time) != 0:
        if int(time) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    pm = request.args.get("pm", 0)
    if int(pm) != 0:
        if int(pm) == 1:
            page_data = page_data.order_by(
                Movie.addtime.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.addtime.asc()
            )
    cm = request.args.get("cm", 0)
    if int(cm) != 0:
        if int(cm) == 1:
            page_data = page_data.order_by(
                Movie.commentnum.desc()
            )
        else:
            page_data = page_data.order_by(
                Movie.commentnum.asc()
            )
    p = dict(
        tid=tid,
        star=star,
        time=time,
        pm=pm,
        cm=cm,
    )
    if page is None:
        page = 1
    page_data = page_data.paginate(page=page, per_page=2)
    return render_template("home/index.html", page_data=page_data, tags=tags, p=p)


@home.route("/animation/")
def animation():
    data = Preview.query.all()
    for v in data:
        print('id', v.id)
        print('logo', v.logo)
        print('title', v.title)
    return render_template("home/animation.html", data=data)


@home.route("/search/<int:page>/", methods=["GET"])
def search(page=None):
    if page is None:
        page = 1
    key = request.args.get("key", "")
    movie_count = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).count()
    page_data = Movie.query.filter(
        Movie.title.ilike('%' + key + '%')
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("home/search.html", movie_count=movie_count, key=key, page_data=page_data)


@home.route("/play/<int:id>/")
def play(id=None):
    movie = Movie.query.join(
        Tag
    ).filter(
        Tag.id == Movie.tag_id,
        Movie.id == int(id)
    ).first_or_404()
    return render_template("home/play.html", movie=movie)
