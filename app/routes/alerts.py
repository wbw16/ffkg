from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from app.models import FloodAlert, River
from app.extensions import db
from app.forms import AlertForm

alert_bp = Blueprint('alert', __name__, url_prefix='/alerts')


@alert_bp.route('/')
def list_alerts():
    # 分页查询 + 搜索过滤
    page = request.args.get('page', 1, type=int)
    river_id = request.args.get('river_id', type=int)

    query = FloodAlert.query.order_by(FloodAlert.timestamp.desc())
    if river_id:
        query = query.filter_by(river_id=river_id)

    alerts = query.paginate(page=page, per_page=20)
    rivers = River.query.all()

    return render_template('alerts/list.html',
                           alerts=alerts,
                           rivers=rivers,
                           current_river_id=river_id)


@alert_bp.route('/create', methods=['GET', 'POST'])
def create_alert():
    form = AlertForm()
    if form.validate_on_submit():
        try:
            alert = FloodAlert(
                river_id=form.river_id.data,
                alert_level=form.alert_level.data,
                description=form.description.data
            )
            db.session.add(alert)
            db.session.commit()
            flash('洪水警报已创建', 'success')
            return redirect(url_for('alert.list_alerts'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('alerts/create.html', form=form)


@alert_bp.route('/<int:alert_id>/edit', methods=['GET', 'POST'])
def edit_alert(alert_id):
    alert = FloodAlert.query.get_or_404(alert_id)
    form = AlertForm(obj=alert)

    if form.validate_on_submit():
        try:
            form.populate_obj(alert)
            db.session.commit()
            flash('警报信息已更新', 'success')
            return redirect(url_for('alert.list_alerts'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('alerts/edit.html', form=form, alert=alert)


@alert_bp.route('/<int:alert_id>/delete', methods=['POST'])
def delete_alert(alert_id):
    alert = FloodAlert.query.get_or_404(alert_id)
    try:
        db.session.delete(alert)
        db.session.commit()
        flash('警报已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('alert.list_alerts'))
