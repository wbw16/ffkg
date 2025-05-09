from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models import User
from app.extensions import db
from app.forms import LoginForm, ChangePasswordForm, ProfileForm  # 添加这行导入
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()  # 创建表单实例

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('无效的用户名或密码')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form)  # 传递form到模板


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


from app.forms import CreateUserForm


@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        flash('无权限操作', 'danger')
        return redirect(url_for('main.index'))

    form = CreateUserForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.create_user'))

        new_user = User(
            username=form.username.data,
            is_admin=form.is_admin.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash(f'用户 {form.username.data} 创建成功', 'success')
        return redirect(url_for('admin.users'))

    return render_template('user/create_user.html', form=form)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        # 检查邮箱是否已被其他用户使用
        if form.email.data != current_user.email:
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('该邮箱已被其他用户使用', 'danger')
                return redirect(url_for('auth.profile'))

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('user/profile.html', form=form)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('当前密码不正确', 'danger')
            return redirect(url_for('auth.change_password'))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('密码已更新', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('user/change_password.html', form=form)