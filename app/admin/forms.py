# coding:utf8

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField, TextAreaField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag, Auth, Role

tags = Tag.query.all()
authss = Auth.query.all()
roles = Role.query.all()


class LoginForm(FlaskForm):
    account = StringField(
        label="account",
        validators=[
            DataRequired("please input account!!")
        ],
        description="account",
        render_kw={
            "class": "form-control",
            "placeholder": "account is required!!",
            # "required": "required",
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("please input password!!")
        ],
        description="password",
        render_kw={
            "class": "form-control",
            "placeholder": "password is required!!",
            # "required": "required"
        }
    )
    submit = SubmitField(
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    def validate_account(self, field):
        account = field.data
        print(account)
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError("account dose not exist!")


class TagForm(FlaskForm):
    name = StringField(
        label="tagname",
        validators=[
            DataRequired("please input a tag name!")
        ],
        description="tag_name",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！"
        }
    )
    submit = SubmitField(
        "input",
        render_kw={
            "class": "btn btn-primary"
        }
    )


class MovieForm(FlaskForm):
    title = StringField(
        label="title",
        validators=[
            DataRequired("please input title")
        ],
        description="title",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！"
        }
    )
    url = FileField(
        label="file",
        validators=[
            DataRequired("please upload file!!!")
        ],
        description="file",
    )
    info = TextAreaField(
        label="brief",
        validators=[
            DataRequired("please input brief!")
        ],
        description="brief",
        render_kw={
            "class": "form-control",
            "rows": "10",
            "id": "input_info"
        }
    )
    logo = FileField(
        label="logo",
        validators=[
            DataRequired("please upload logo!!!")
        ],
        description="logo",
    )
    star = SelectField(
        label="star",
        validators=[
            DataRequired("please input brief!")
        ],
        coerce=int,
        choices=[(1, "1星"), (2, "2星"), (3, "3星"), (4, "4星"), (5, "5星")],
        description="star",
        render_kw={
            "class": "form-control",
            "id": "input_star"
        }
    )
    tag_id = SelectField(
        label="tag",
        validators=[
            DataRequired("please select a tag!")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        description="tag",
        render_kw={
            "class": "form-control",
            "id": "input_tag_id"
        }
    )
    area = StringField(
        label="area",
        validators=[
            DataRequired("please input a area!")
        ],
        description="area",
        render_kw={
            "class": "form-control",
            "id": "input_area",
            "placeholder": "请输入地区！"
        }
    )
    length = StringField(
        label="length",
        validators=[
            DataRequired("please input a length!")
        ],
        description="length",
        render_kw={
            "class": "form-control",
            "id": "input_length",
            "placeholder": "请输入片长！"
        }
    )
    release_time = StringField(
        label="release_time",
        validators=[
            DataRequired("please select release_time!!")
        ],
        description="release_time",
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间！",
            "id": "input_release_time"
        }
    )
    submit = SubmitField(
        'upload',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class PreviewForm(FlaskForm):
    title = StringField(
        label="title",
        validators=[
            DataRequired("please input title")
        ],
        description="title",
        render_kw={
            "class": "form-control",
            "id": "input_title",
            "placeholder": "请输入片名！"
        }
    )
    logo = FileField(
        label="logo",
        validators=[
            DataRequired("please upload logo!!!")
        ],
        description="logo",
    )
    submit = SubmitField(
        'upload',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="old_password",
        validators=[
            DataRequired("please input old password!")
        ],
        description="old_passwordddddd",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入旧密码！"
        }
    )
    new_pwd = PasswordField(
        label="new_password",
        validators=[
            DataRequired("please input new password!")
        ],
        description="new_passwordddddd",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入新密码！"
        }
    )
    submit = SubmitField(
        'upload',
        render_kw={
            "class": "btn btn-primary",
        }
    )

    def validate_old_pwd(self, field):
        print('field', field)
        from flask import session
        pwd = field.data
        name = session["admin"]
        admin = Admin.query.filter_by(
            name=name
        ).first()
        if not admin.check_pwd(pwd):
            raise ValidationError("old password is not correct!!")


class AuthForm(FlaskForm):
    name = StringField(
        label="auth_name",
        validators=[
            DataRequired("please input the auth_name"),
        ],
        description="it's the authrization's name",
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限名称！"
        }
    )
    url = StringField(
        label="auth_url",
        validators=[
            DataRequired("please input auth_url"),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入权限地址！"
        }
    )
    sutmit = SubmitField(
        'submit',
        render_kw={
            "class": "btn btn-primary",
        }
    )


class RoleForm(FlaskForm):
    name = StringField(
        label="name",
        validators=[
            DataRequired("please input the role name"),
        ],
        description="role's name",
        render_kw={
            'class': "form-control",
            "id": "input_name",
            "placeholder": "请输入角色名称！",
        }
    )
    auths = SelectMultipleField(
        label="auth",
        validators=[
            DataRequired("please select an auth!")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in authss],
        description="tag",
        render_kw={
            "class": "form-control",
            "id": "input_tag_id"
        }
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-primary",
        }
    )


class AdminForm(FlaskForm):
    name = StringField(
        label="admin name",
        validators=[
            DataRequired("please input an admin name")
        ],
        description="admin's name",
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入管理员名称！"
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("please input a password!"),
        ],
        description="admin's password",
        render_kw={
            "class": "form-control",
            "id": "input_pwd",
            "placeholder": "请输入管理员密码！"
        }
    )
    repwd = PasswordField(
        label="repassword",
        validators=[
            DataRequired("please input a password again!"),
            EqualTo('pwd', message="repwd is not as same as pwd!!"),
        ],
        description="admin's repassword",
        render_kw={
            "class": "form-control",
            "id": "input_pwd",
            "placeholder": "请输入管理员密码！"
        }
    )
    role_id = SelectField(
        label="role_id",
        validators=[
            DataRequired("please select a role's id!!"),
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in roles],
        description="role's id",
        render_kw={
            "class": "form-control",
            "id": "input_role_id"
        }
    )
    submit = SubmitField(
        label="submit",
        render_kw={
            "class": "btn btn-primary",
        }
    )
