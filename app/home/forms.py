# coding:utf8
from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, PasswordField, StringField, TextAreaField, SelectMultipleField, SelectField, \
    FileField
from wtforms.validators import DataRequired, EqualTo, Email, Regexp, ValidationError
from app.models import User


class RegistForm(FlaskForm):
    name = StringField(
        label="nickname",
        validators=[
            DataRequired("please input your nickname"),
        ],
        description="nick name!",
        render_kw={
            'id': "input_name",
            "class": "form-control input-lg",
            "placeholder": "昵称",
        }
    )
    email = StringField(
        label="email box",
        validators=[
            DataRequired("please input your email"),
            Email("email box is not valid!"),
        ],
        description="email box",
        render_kw={
            "id": "input_email",
            "class": "form-control input-lg",
            "placeholder": "邮箱",
        }
    )
    phone = StringField(
        label="phone",
        validators=[
            DataRequired("please input your phone number"),
            Regexp("1[3458]\\d{9}", message="cell phone format is not valid!")
        ],
        description="phone number",
        render_kw={
            "id": "input_phone",
            "class": "form-control input-lg",
            "placeholder": "手机"
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("please input your password"),
        ],
        description="password",
        render_kw={
            "id": "input_password",
            "class": "form-control input-lg",
            "placeholder": "密码",
        }
    )
    re_pwd = PasswordField(
        label="re_password",
        validators=[
            DataRequired("please input your re_password"),
            EqualTo("pwd", message="two passwords are not the same!!")
        ],
        description="re_password",
        render_kw={
            "id": "input_repassword",
            "class": "form-control input-lg",
            "placeholder": "确认密码",
        }
    )
    submit = SubmitField(
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )

    def validate_name(self, field):
        name = field.data
        user = User.query.filter_by(name=name).count()
        if user == 1:
            raise ValidationError("the user already exists!!!")

    def validate_email(self, field):
        email = field.data
        email = User.query.filter_by(email=email).count()
        if email == 1:
            raise ValidationError("the email already exists!!!")

    def validate_phone(self, field):
        phone = field.data
        phone = User.query.filter_by(phone=phone).count()
        if phone == 1:
            raise ValidationError("the phone already exists!!!")


class LoginForm(FlaskForm):
    name = StringField(
        label="acount",
        validators=[
            DataRequired("please input your account"),
        ],
        description="account!",
        render_kw={
            'id': "input_contact",
            "class": "form-control input-lg",
            "placeholder": "用户名/邮箱/手机号码",
        }
    )
    pwd = PasswordField(
        label="password",
        validators=[
            DataRequired("please input your password"),
        ],
        description="password",
        render_kw={
            "id": "input_password",
            "class": "form-control input-lg",
            "placeholder": "密码",
        }
    )
    submit = SubmitField(
        render_kw={
            "class": "btn btn-lg btn-success btn-block"
        }
    )


class UserdetailForm(FlaskForm):
    name = StringField(
        label="acount",
        validators=[
            DataRequired("please input your account"),
        ],
        description="account!",
        render_kw={
            'id': "input_name",
            "class": "form-control",
            "placeholder": "昵称",
        }
    )
    email = StringField(
        label="email box",
        validators=[
            DataRequired("please input your email"),
            Email("email box is not valid!"),
        ],
        description="email box",
        render_kw={
            "id": "input_email",
            "class": "form-control",
            "placeholder": "邮箱",
        }
    )
    phone = StringField(
        label="phone",
        validators=[
            DataRequired("please input your phone number"),
            Regexp("1[3458]\\d{9}", message="cell phone format is not valid!")
        ],
        description="phone number",
        render_kw={
            "id": "input_phone",
            "class": "form-control input-lg",
            "placeholder": "手机"
        }
    )
    face = FileField(
        label="face",
        validators=[
            DataRequired("please upload your head image!"),
        ],
        description="face",
    )
    info = TextAreaField(
        label="brief",
        validators=[
            DataRequired("please input your brief"),
        ],
        description="brief",
        render_kw={
            "class": "form-control",
            "rows": "10",
            "id": "input_info"
        }
    )
    submit = SubmitField(
        '<span class="glyphicon glyphicon-saved">&nbsp;保存修改</span>',
        render_kw={
            "class": "btn btn-success"
        }
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="old password",
        validators=[
            DataRequired("please input old password!"),
        ],
        description="old_password",
        render_kw={
            "id": "input_oldpwd",
            "class": "form-control",
            "placeholder": "旧密码",
        }
    )
    new_pwd = PasswordField(
        label="new password",
        validators=[
            DataRequired("please input new password"),
        ],
        description="new_password",
        render_kw={
            "id": "input_newpwd",
            "class": "form-control",
            "placeholder": "新密码",
        }
    )
    submit = SubmitField(
        "changePWD",
        render_kw={
            "class": "btn btn-success"
        }
    )
