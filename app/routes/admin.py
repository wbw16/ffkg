from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import User
from app.forms import UserForm
from app.extensions import db

admin_bp = Blueprint('admin', __name__,url_prefix='/admin')


@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('无权访问该页面', 'danger')
        return redirect(url_for('main.index'))

    users = User.query.order_by(User.id).all()
    return render_template('user/users.html', users=users)


@admin_bp.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('无权访问该页面', 'danger')
        return redirect(url_for('main.index'))

    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=form.is_admin.data,
            active=form.active.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('用户添加成功', 'success')
        return redirect(url_for('admin.users'))

    return render_template('user/user_form.html', form=form)


@admin_bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('无权访问该页面', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        user.active = form.active.data
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin.users'))

    return render_template('user/user_form.html', form=form, user=user)


@admin_bp.route('/user/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('无权访问该页面', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('不能删除管理员账户', 'warning')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('用户已删除', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/user/deactivate/<int:user_id>', methods=['POST'])
@login_required
def deactivate_user(user_id):
    if not current_user.is_admin:
        abort(403)

    user = User.query.get_or_404(user_id)
    user.active = False
    db.session.commit()
    flash(f'用户 {user.username} 已停用', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('您没有访问此页面的权限', 'danger')
        return redirect(url_for('main.index'))

    # 获取一些统计信息
    total_users = User.query.count()
    new_users = User.query.filter(
        User.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()

    return render_template('user/dashboard.html',
                           total_users=total_users,
                           new_users=new_users)