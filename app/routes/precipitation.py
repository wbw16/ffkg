from crypt import methods

from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required
from app.models import PrecipitationData, WeatherStation
from app.extensions import db
from app.forms import PrecipitationForm
from datetime import datetime, timedelta

precip_bp = Blueprint('precip', __name__, url_prefix='/precipitation')  # 注意第一个参数是蓝本名称

@precip_bp.route('/')
def list_precipitation():
    page = request.args.get('page', 1, type=int)
    station_id = request.args.get('station_id', type=int)
    date_filter = request.args.get('date', type=str)

    query = PrecipitationData.query.order_by(PrecipitationData.timestamp.desc())

    # 筛选条件
    if station_id:
        query = query.filter_by(station_id=station_id)
    if date_filter:
        try:
            date_obj = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(db.func.date(PrecipitationData.timestamp) == date_obj)
        except ValueError:
            flash('日期格式无效', 'warning')

    records = query.paginate(page=page, per_page=20)
    stations = WeatherStation.query.order_by(WeatherStation.name).all()

    return render_template('precipitation/list.html',
                           records=records,
                           stations=stations,
                           current_station_id=station_id,
                           current_date=date_filter)


@precip_bp.route('/create', methods=['GET', 'POST'])
def create_record():
    form = PrecipitationForm()
    if form.validate_on_submit():
        try:
            record = PrecipitationData(
                station_id=form.station_id.data,
                amount=float(form.amount.data),
                timestamp=form.timestamp.data or datetime.utcnow()
            )
            db.session.add(record)
            db.session.commit()
            flash('降水记录已添加', 'success')
            return redirect(url_for('precipitation.list_precipitation'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}', 'danger')

    return render_template('precipitation/create.html', form=form)


from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import PrecipitationData, WeatherStation
from app.extensions import db
from app.forms import PrecipitationForm


# ...之前的路由保持不变...

@precip_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
def edit_record(record_id):
    record = PrecipitationData.query.get_or_404(record_id)
    form = PrecipitationForm(obj=record)

    if request.method == 'GET':
        # 初始化时间字段格式
        form.timestamp.data = record.timestamp.strftime('%Y-%m-%d %H:%M')

    if form.validate_on_submit():
        try:
            original_amount = record.amount
            form.populate_obj(record)
            record.editor_id = current_user.id  # 记录修改人

            # 检查数据变更
            changes = {
                'field': 'precipitation',
                'old_value': original_amount,
                'new_value': record.amount,
                'editor': current_user.username
            }

            db.session.commit()
            flash(f'记录已更新. 变更: {changes}', 'success')
            return redirect(url_for('precipitation.list_precipitation'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    # 获取气象站列表（避免模板中直接查询数据库）
    stations = [(s.station_id, f"{s.name} ({s.code})")
                for s in WeatherStation.query.order_by(WeatherStation.name).all()]

    return render_template('precipitation/edit.html',
                           form=form,
                           record=record,
                           stations=stations)


@precip_bp.route('/<int:record_id>/delete', methods=['POST'])
 
def delete_record(record_id):
    record = PrecipitationData.query.get_or_404(record_id)
    try:
        # 记录删除日志
        deletion_log = {
            'deleted_data': {
                'station': record.station.name,
                'amount': record.amount,
                'time': record.timestamp.isoformat()
            },
            'deleted_by': current_user.username,
            'deleted_at': datetime.utcnow().isoformat()
        }

        db.session.delete(record)
        db.session.commit()
        flash(f'记录已删除. 日志: {deletion_log}', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('precipitation.list_precipitation'))


# 数据导出接口
@precip_bp.route('/export')
 
def export_data():
    format = request.args.get('format', 'json')

    # 可以根据需要添加更多筛选条件
    records = PrecipitationData.query.order_by(PrecipitationData.timestamp.desc()).all()

    if format == 'csv':
        # 实现CSV导出逻辑...
        pass
    else:
        return jsonify([{
            'station': record.station.name,
            'timestamp': record.timestamp.isoformat(),
            'amount': record.amount,
            'recorded_by': record.creator.username if record.creator else None
        } for record in records])


@precip_bp.route('/api/chart')
def precipitation_chart():
    station_id = request.args.get('station_id', type=int)
    days = request.args.get('days', default=7, type=int)

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    query = PrecipitationData.query.filter(
        PrecipitationData.timestamp >= start_date,
        PrecipitationData.station_id == station_id
    ).order_by(PrecipitationData.timestamp)

    return jsonify([{
        'x': record.timestamp.isoformat(),
        'y': float(record.amount)
    } for record in query.all()])

