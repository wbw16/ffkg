from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db, FloodControlStrategy, River
from app.forms import FloodControlStrategyForm
import json

flood_control_bp = Blueprint('flood_control', __name__, url_prefix='/flood-control-strategies')


@flood_control_bp.route('/')
def list_strategies():
    page = request.args.get('page', 1, type=int)
    river_id = request.args.get('river_id', type=int)
    alert_level = request.args.get('alert_level', type=str)

    query = FloodControlStrategy.query.order_by(FloodControlStrategy.river_id.asc())

    if river_id:
        query = query.filter_by(river_id=river_id)
    if alert_level:
        query = query.filter_by(alert_level=alert_level)

    strategies = query.paginate(page=page, per_page=10)
    rivers = River.query.order_by(River.name).all()

    return render_template('flood_control_strategies/list.html',
                           strategies=strategies,
                           rivers=rivers,
                           alert_level=alert_level,
                           current_river_id=river_id)


@flood_control_bp.route('/create', methods=['GET', 'POST'])
def create_strategy():
    form = FloodControlStrategyForm()

    if form.validate_on_submit():
        try:
            # 处理联系人JSON数据
            contacts = []
            for i in range(1, 4):
                name = request.form.get(f'contact_name_{i}')
                phone = request.form.get(f'contact_phone_{i}')
                if name and phone:
                    contacts.append({"name": name, "phone": phone})

            strategy = FloodControlStrategy(
                river_id=form.river_id.data,
                alert_level=form.alert_level.data,
                action_plan=form.action_plan.data,
                contact_persons=json.dumps(contacts, ensure_ascii=False)
            )
            db.session.add(strategy)
            db.session.commit()
            flash('防洪预案已创建成功', 'success')
            return redirect(url_for('flood_control.list_strategies'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('flood_control_strategies/create.html', form=form)


@flood_control_bp.route('/<int:strategy_id>/edit', methods=['GET', 'POST'])
 
def edit_strategy(strategy_id):
    strategy = FloodControlStrategy.query.get_or_404(strategy_id)
    form = FloodControlStrategyForm(obj=strategy)
    contacts = json.loads(strategy.contact_persons) if strategy.contact_persons else []

    if form.validate_on_submit():
        try:
            # 更新联系人数据
            updated_contacts = []
            for i in range(1, 4):
                name = request.form.get(f'contact_name_{i}')
                phone = request.form.get(f'contact_phone_{i}')
                if name and phone:
                    updated_contacts.append({"name": name, "phone": phone})

            form.populate_obj(strategy)
            strategy.contact_persons = json.dumps(updated_contacts, ensure_ascii=False)
            db.session.commit()
            flash('防洪预案已更新', 'success')
            return redirect(url_for('flood_control.list_strategies'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('flood_control_strategies/edit.html',
                           form=form,
                           strategy=strategy,
                           contacts=contacts)


@flood_control_bp.route('/<int:strategy_id>/delete', methods=['POST'])
 
def delete_strategy(strategy_id):
    strategy = FloodControlStrategy.query.get_or_404(strategy_id)
    try:
        db.session.delete(strategy)
        db.session.commit()
        flash(f'[{strategy.river.name}]的预案已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('flood_control.list_strategies'))
