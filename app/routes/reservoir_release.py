from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required
from app.models import ReservoirReleaseData, Reservoir
from app.extensions import db
from app.forms import ReleaseForm
from datetime import datetime, timedelta

release_bp = Blueprint('reservoir_release', __name__, url_prefix='/reservoir-releases')


@release_bp.route('/')
def list_releases():
    page = request.args.get('page', 1, type=int)
    reservoir_id = request.args.get('reservoir_id', type=int)

    query = ReservoirReleaseData.query.order_by(ReservoirReleaseData.timestamp.desc())
    if reservoir_id:
        query = query.filter_by(reservoir_id=reservoir_id)

    releases = query.paginate(page=page, per_page=20)
    reservoirs = Reservoir.query.all()

    return render_template('reservoir_releases/list.html',
                           releases=releases,
                           reservoirs=reservoirs,
                           current_reservoir_id=reservoir_id)


@release_bp.route('/create', methods=['GET', 'POST'])
def create_release():
    form = ReleaseForm()
    if form.validate_on_submit():
        try:
            release = ReservoirReleaseData(
                reservoir_id=form.reservoir_id.data,
                release_amount=form.amount.data,
                timestamp=form.timestamp.data or datetime.utcnow()
            )
            db.session.add(release)
            db.session.commit()
            flash('放水记录已添加', 'success')
            return redirect(url_for('reservoir_release.list_releases'))
        except Exception as e:
            db.session.rollback()
            flash(f'添加失败: {str(e)}', 'danger')

    return render_template('reservoir_releases/create.html', form=form)


@release_bp.route('/<int:release_id>/edit', methods=['GET', 'POST'])
def edit_release(release_id):
    release = ReservoirReleaseData.query.get_or_404(release_id)
    form = ReleaseForm(obj=release)

    if form.validate_on_submit():
        try:
            form.populate_obj(release)
            db.session.commit()
            flash('记录已更新', 'success')
            return redirect(url_for('reservoir_release.list_releases'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('reservoir_releases/edit.html',
                           form=form,
                           release=release)


@release_bp.route('/<int:release_id>/delete', methods=['POST'])
def delete_release(release_id):
    release = ReservoirReleaseData.query.get_or_404(release_id)
    try:
        db.session.delete(release)
        db.session.commit()
        flash('记录已删除', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('reservoir_release.list_releases'))
