# coding:utf8

import os
from . import admin
from flask import render_template, redirect, url_for, flash, session, request, abort
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm, AdminForm
from app.models import Admin, Tag, Movie, Preview, User, Comment, Moviecol, Auth, Role
from functools import wraps
from app import db, app
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime


def admin_login_req(f):
    @wraps(f)
    def decrated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)

    return decrated_function


def admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin = Admin.query.join(
            Role
        ).filter(
            Admin.role_id == Role.id,
            # Admin.id == session["admin_id"]
        ).first()
        auths = admin.role.auths
        print('auths', auths)
        auths = list(map(lambda v: int(v), auths.split(",")))
        auth_list = Auth.query.all()
        urls = [v.url for v in auth_list for val in auths if val == v.id]
        rule = request.url_rule
        if rule not in urls:
            abort(404)
        return f(*args, **kwargs)

    return decorated_function


def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + fileinfo[-1]
    return filename


@admin.route("/")
@admin_login_req
# @admin_auth
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print('login_form', form.data)
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("password is not correct!")
            return redirect(url_for("admin.login"))
        session["admin"] = data["account"]
        session["admin_id"] = admin.id
        return redirect(request.args.get("next") or url_for("admin.index"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop("admin", None)
    session.pop("admin_id", None)
    return redirect(url_for("admin.login"))


@admin.route("/pwd/", methods=["GET", "POST"])
@admin_login_req
def pwd():
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=session["admin"]).first()
        from werkzeug.security import generate_password_hash
        admin.pwd = generate_password_hash(data["new_pwd"])
        db.session.add(admin)
        db.session.commit()
        flash("password has been changed successfully!, please login again", "ok")
        return redirect(url_for('admin.logout'))
    return render_template("admin/pwd.html", form=form)


@admin.route("/tag/add/", methods=['GET', 'POST'])
@admin_login_req
# @admin_auth
def tag_add():
    form = TagForm()
    print('tag_form', form.data)
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data["name"]).count()
        if tag == 1:
            flash("the tag already exists!!", "error")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data["name"],
        )
        db.session.add(tag)
        db.session.commit()
        flash("tag added succesfully!", "ok")
        redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
# @admin_auth
def tag_list(page=None):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/tag_list.html", page_data=page_data)


# tag_delete
@admin.route("/tag/del/<int:id>/", methods=["GET"])
@admin_login_req
# @admin_auth
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("delete successfully!", "ok")
    return redirect(url_for('admin.tag_list', page=1))


# tag_edit
@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
# @admin_auth
def tag_edit(id=None):
    form = TagForm()
    tag = Tag.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        data = form.data
        print('tag_edit_data', data)
        tag_count = Tag.query.filter_by(name=data["name"]).count()
        if tag.name != data["name"] and tag_count == 1:
            flash("the tag already exists!!", "error")
            return redirect(url_for("admin.tag_edit", id=tag.id))
        tag.name = data["name"]
        db.session.add(tag)
        db.session.commit()
        flash("tag updated succesfully!", "ok")
        redirect(url_for('admin.tag_edit', id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


@admin.route("/movie/add/", methods=["GET", "POST"])
@admin_login_req
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 755)
        url = change_filename(file_url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        movie = Movie(
            title=data["title"],
            url=url,
            info=data["info"],
            logo=logo,
            star=int(data["star"]),
            playnum=0,
            tag_id=int(data["tag_id"]),
            area=data["area"],
            release_time=data["release_time"],
            length=data["length"]
        )
        db.session.add(movie)
        db.session.commit()
        flash("movie added successfully!", "ok")
        return redirect(url_for('admin.movie_add'))
    return render_template("admin/movie_add.html", form=form)


@admin.route("/movie/list/<int:page>/", methods=['GET'])
@admin_login_req
def movie_list(page=None):
    if page is None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/movie_list.html", page_data=page_data)


@admin.route("/movie/del/<int:id>/", methods=['GET'])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.filter_by(id=id).first_or_404()
    db.session.delete(movie)
    db.session.commit()
    flash("movie delete successfully!!", "ok")
    return redirect(url_for('admin.movie_list', page=1))


# edit movie
@admin.route("/movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id=None):
    form = MovieForm()
    movie = Movie.query.get_or_404(int(id))
    if request.method == "GET":
        form.info.data = movie.info
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data["title"]).count()
        if movie_count == 1 and movie.title != data["title"]:
            flash("this movie already exists!!", "error")
            return redirect(url_for('admin.movie_edit', id=id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 777)

        if form.url.data.filename != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + movie.logo)

        movie.star = data["star"]
        movie.tag_id = data["tag_id"]
        movie.info = data["info"]
        movie.title = data["title"]
        movie.area = data["area"]
        movie.length = data["length"]
        movie.release_time = data["release_time"]
        db.session.add(movie)
        db.session.commit()
        flash("movie edited successfully!", "ok")
        return redirect(url_for('admin.movie_list', page=1))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


@admin.route("/preview/add/", methods=['GET', 'POST'])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], 755)
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)

        preview = Preview(
            title=data["title"],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("preview added successfully!", "ok")
        return redirect(url_for('admin.preview_add'))
    return render_template("admin/preview_add.html", form=form)


@admin.route("/preview/list/<int:page>/", methods=['GET'])
@admin_login_req
def preview_list(page=None):
    if page is None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/preview_list.html", page_data=page_data)


@admin.route("/preview/del/<int:id>/", methods=['GET'])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.filter_by(id=id).first_or_404()
    db.session.delete(preview)
    db.session.commit()
    flash("preview deleted!!!", "ok")
    return redirect(url_for('admin.preview_list', page=1))


@admin.route("/preview/edit/<int:id>", methods=['GET', 'POST'])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    print('preview_edit_form', form.data)
    form.logo.validators = []
    preview = Preview.query.get_or_404(int(id))
    print('preview', preview)
    if form.validate_on_submit():
        data = form.data
        print('form.logo.data', form.logo.data)
        if form.logo.data.filename != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config["UP_DIR"] + preview.logo)

        preview.title = data["title"]
        db.session.add(preview)
        db.session.commit()
        flash("preview added successfully!", "ok")
        return redirect(url_for('admin.preview_edit', id=id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


@admin.route("/user/list/<int:page>/", methods=["GET"])
@admin_login_req
def user_list(page=None):
    if page is None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/user_list.html", page_data=page_data)


@admin.route("/user/view/<int:id>", methods=["GET"])
@admin_login_req
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user)


@admin.route("/user/del/<int:id>", methods=["GET"])
@admin_login_req
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("user succesfully deleted!!", "ok")
    return redirect(url_for('admin.user_list', page=1))


@admin.route("/comment/list/<int:page>/", methods=["GET"])
@admin_login_req
def comment_list(page=None):
    if page == None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id,
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/comment_list.html", page_data=page_data)


@admin.route("/comment/del/<int:id>", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("comment succesfully deleted!!", "ok")
    return redirect(url_for('admin.comment_list', page=1))


@admin.route("/moviecol/list/<int:page>/", methods=["GET"])
@admin_login_req
def moviecol_list(page=None):
    if page == None:
        page = 1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id,
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=2)
    print(page_data)
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route("/moviecol/del/<int:id>/", methods=["GET"])
@admin_login_req
def moviecol_del(id=None):
    moviecol = Moviecol.query.filter_by(id=id).first_or_404()
    db.session.delete(moviecol)
    db.session.commit()
    flash("delete of moviecol is successful!", "ok")
    return redirect(url_for("admin.moviecol_list", page=1))


@admin.route("/oplog/list/")
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")


@admin.route("/adminloginlog/list/")
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")


@admin.route("/userloginlog/list/")
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")


@admin.route("/role/add/", methods=["GET", "POST"])
@admin_login_req
def role_add():
    form = RoleForm()
    if form.validate_on_submit():
        data = form.data
        print(data)
        role = Role(
            name=data["name"],
            auths=",".join(map(lambda v: str(v), data["auths"])),
        )
        db.session.add(role)
        db.session.commit()
        flash("role is successfully added!", "ok")
        return redirect(url_for("admin.role_add"))
    return render_template("admin/role_add.html", form=form)


@admin.route("/role/list/<int:page>/", methods=["GET"])
@admin_login_req
def role_list(page=None):
    if page is None:
        page = 1
    page_data = Role.query.order_by(
        Role.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/role_list.html", page_data=page_data)


@admin.route("/auth/add/", methods=["GET", "POST"])
@admin_login_req
def auth_add():
    form = AuthForm()
    if form.validate_on_submit():
        data = form.data
        auth = Auth(
            name=data["name"],
            url=data["url"],
        )
        db.session.add(auth)
        db.session.commit()
        flash("the auth is added successfully!", "ok")
    return render_template("admin/auth_add.html", form=form)


@admin.route("/role/del/<int:id>/", methods=["GET"])
@admin_login_req
def role_del(id=None):
    role = Role.query.filter_by(id=id).first_or_404()
    db.session.delete(role)
    db.session.commit()
    flash("role deletion is done!", "ok")
    return redirect(url_for("admin.role_list", page=1))


@admin.route("/role/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def role_edit(id):
    form = RoleForm()
    role = Role.query.filter_by(id=id).first_or_404()
    if request.method == "GET":
        auths = role.auths
        form.auths.data = list(map(lambda v: int(v), auths.split(",")))
    if form.validate_on_submit():
        role.name = form.data["name"],
        role.auths = ",".join(map(lambda v: str(v), form.data["auths"]))
        db.session.add(role)
        db.session.commit()
        flash("role edited successfully!", "ok")
        return redirect(url_for("admin.role_list", page=1))
    return render_template("admin/role_edit.html", form=form, role=role)


@admin.route("/auth/list/<int:page>/", methods=["GET"])
@admin_login_req
def auth_list(page=None):
    if page is None:
        page = 1
    page_data = Auth.query.order_by(
        Auth.addtime.desc()
    ).paginate(page=page, per_page=2)
    return render_template("admin/auth_list.html", page_data=page_data)


# auth_delete
@admin.route("/auth/del/<int:id>/", methods=["GET"])
@admin_login_req
def auth_del(id=None):
    auth = Auth.query.filter_by(id=id).first_or_404()
    db.session.delete(auth)
    db.session.commit()
    flash("delete successfully!", "ok")
    return redirect(url_for('admin.auth_list', page=1))


# auth_edit
@admin.route("auth/eidt/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def auth_edit(id):
    form = AuthForm()
    auth = Auth.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        data = form.data
        auth.name = data["name"]
        auth.url = data["url"]
        db.session.add(auth)
        db.session.commit()
        flash("auth edited successfully!", "ok")
        return redirect(url_for('admin.auth_list', page=1))
    return render_template("admin/auth_edit.html", form=form, auth=auth)


@admin.route("/admin/add/", methods=["GET", "POST"])
@admin_login_req
def admin_add():
    form = AdminForm()
    from werkzeug.security import generate_password_hash
    if form.validate_on_submit():
        data = form.data
        admin = Admin(
            name=data["name"],
            pwd=generate_password_hash(data["pwd"]),
            is_super=1,
            role_id=data["role_id"],
        )
        db.session.add(admin)
        db.session.commit()
        flash("admin added successfully!", "ok")
    return render_template("admin/admin_add.html", form=form)


@admin.route("/admin/list/<int:page>", methods=["GET"])
@admin_login_req
def admin_list(page=None):
    if page is None:
        page = 1
    page_data = Admin.query.join(Role).filter(Role.id == Admin.role_id).order_by(Admin.addtime.desc()).paginate(
        page=page, per_page=2)
    for v in page_data.items:
        print(v.name)
    return render_template("admin/admin_list.html", page_data=page_data)
