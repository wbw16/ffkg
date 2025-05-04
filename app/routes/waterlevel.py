from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import WaterLevelData, MonitoringStation, River
from app.extensions import db
from app.forms import WaterLevelForm

water_bp = Blueprint('water_level', __name__, url_prefix='/water-levels')


@water_bp.route('/')
def list_water_levels():
    page = request.args.get('page', 1, type=int)
    station_id = request.args.get('station_id', type=int)
    alert_only = request.args.get('alert_only', False, type=bool)

    query = WaterLevelData.query.join(MonitoringStation).order_by(
        WaterLevelData.timestamp.desc()
    )

    # 筛选条件
    if station_id:
        query = query.filter_by(monitor_id=station_id)
    if alert_only:
        query = query.join(MonitoringStation).filter(
            WaterLevelData.level >= MonitoringStation.warning_level
        )

    records = query.paginate(page=page, per_page=20)
    stations = MonitoringStation.query.options(
        db.joinedload(MonitoringStation.river)
    ).order_by(MonitoringStation.name).all()

    return render_template('water_levels/list.html',
                           records=records,
                           stations=stations,
                           current_station_id=station_id,
                           alert_only=alert_only)


@water_bp.route('/create', methods=['GET', 'POST'])
 
def create_record():
    form = WaterLevelForm()

    if form.validate_on_submit():
        try:
            record = WaterLevelData(
                monitor_id=form.monitor_id.data,
                level=form.level.data,
                timestamp=form.timestamp.data or datetime.utcnow(),
                creator_id=current_user.id,
                notes=form.notes.data
            )

            # 检查是否超过警戒水位
            station = MonitoringStation.query.get(form.monitor_id.data)
            if station and station.warning_level and form.level.data >= station.warning_level:
                record.is_alert = True
                flash('⚠️ 水位已超过警戒线！', 'warning')

            db.session.add(record)
            db.session.commit()
            flash('水位记录已添加', 'success')
            return redirect(url_for('water_level.list_water_levels'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}', 'danger')

    return render_template('water_levels/create.html', form=form)


@water_bp.route('/<int:record_id>/edit', methods=['GET', 'POST'])
 
def edit_record(record_id):
    record = WaterLevelData.query.options(
        db.joinedload(WaterLevelData.monitor)
    ).get_or_404(record_id)

    form = WaterLevelForm(obj=record)
    form.monitor_id.choices = [(m.monitor_id, f"{m.name} ({m.river.name})")
                               for m in MonitoringStation.query.all()]

    if form.validate_on_submit():
        try:
            original_level = record.level
            form.populate_obj(record)
            record.editor_id = current_user.id

            # 重新检查警戒状态
            if record.level >= record.monitor.warning_level:
                record.is_alert = True
                flash('水位已超过警戒线！', 'warning')
            else:
                record.is_alert = False

            db.session.commit()
            flash(f'水位记录已更新 (原值: {original_level:.2f}m)', 'success')
            return redirect(url_for('water_level.list_water_levels'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('water_levels/edit.html',
                           form=form,
                           record=record,
                           warning_level=record.monitor.warning_level)


@water_bp.route('/<int:record_id>/delete', methods=['POST'])
 
def delete_record(record_id):
    record = WaterLevelData.query.get_or_404(record_id)
    try:
        station_name = record.monitor.name
        db.session.delete(record)
        db.session.commit()
        flash(f'已删除 {station_name} 的水位记录 (原值: {record.level:.2f}m)', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('water_level.list_water_levels'))


@water_bp.route('/api/trend')
def water_level_trend():
    station_id = request.args.get('station_id', type=int)
    days = request.args.get('days', default=30, type=int)

    station = MonitoringStation.query.get_or_404(station_id)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    records = WaterLevelData.query.filter(
        WaterLevelData.monitor_id == station_id,
        WaterLevelData.timestamp.between(start_date, end_date)
    ).order_by(WaterLevelData.timestamp).all()

    return jsonify({
        'station': station.name,
        'river': station.river.name,
        'warning_level': float(station.warning_level) if station.warning_level else None,
        'data': [{
            'x': r.timestamp.isoformat(),
            'y': float(r.level),
            'alert': r.is_alert
        } for r in records]
    })
