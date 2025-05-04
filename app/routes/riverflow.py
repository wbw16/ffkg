from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.models import db, RiverFlowData, River
from app.forms import RiverFlowForm

river_flow_bp = Blueprint('river_flow', __name__, url_prefix='/river-flows')


@river_flow_bp.route('/')
def list_flows():
    # 查询参数处理
    river_id = request.args.get('river_id', type=int)
    date_range = request.args.get('date_range', 'today')
    page = request.args.get('page', 1, type=int)

    # 构建基础查询
    query = RiverFlowData.query.order_by(RiverFlowData.timestamp.desc())

    # 过滤条件
    if river_id:
        query = query.filter_by(river_id=river_id)

    # 时间范围筛选
    if date_range == 'today':
        today = datetime.utcnow().date()
        query = query.filter(RiverFlowData.timestamp >= today)
    elif date_range == 'week':
        week_ago = datetime.utcnow() - timedelta(days=7)
        query = query.filter(RiverFlowData.timestamp >= week_ago)

    # 分页查询
    flows = query.paginate(page=page, per_page=20)

    # 相关数据
    rivers = River.query.order_by(River.name).all()

    return render_template('river_flows/list.html',
                           flows=flows,
                           rivers=rivers,
                           current_river_id=river_id,
                           date_range=date_range)


@river_flow_bp.route('/create', methods=['GET', 'POST'])
 
def create_flow():
    form = RiverFlowForm()

    if form.validate_on_submit():
        try:
            flow = RiverFlowData(
                river_id=form.river_id.data,
                flow_rate=form.flow_rate.data,
                timestamp=form.timestamp.data or datetime.utcnow()
            )
            db.session.add(flow)
            db.session.commit()
            flash('河流流量记录已创建成功', 'success')
            return redirect(url_for('river_flow.list_flows'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('river_flows/create.html', form=form)


@river_flow_bp.route('/<int:flow_id>/edit', methods=['GET', 'POST'])
 
def edit_flow(flow_id):
    flow = RiverFlowData.query.get_or_404(flow_id)
    form = RiverFlowForm(obj=flow)

    if form.validate_on_submit():
        try:
            form.populate_obj(flow)
            db.session.commit()
            flash('流量记录已更新', 'success')
            return redirect(url_for('river_flow.list_flows'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('river_flows/edit.html',
                           form=form,
                           flow=flow)


@river_flow_bp.route('/<int:flow_id>/delete', methods=['POST'])
 
def delete_flow(flow_id):
    flow = RiverFlowData.query.get_or_404(flow_id)
    try:
        db.session.delete(flow)
        db.session.commit()
        flash(f'{flow.river.name}的流量记录已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('river_flow.list_flows'))
