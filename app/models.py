from app.extensions import db
from datetime import datetime, timedelta


class Basin(db.Model):
    """流域模型"""
    __tablename__ = 'basins'
    basin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    area = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    rivers = db.relationship('River', back_populates='basin', cascade='all, delete-orphan')
    weather_stations = db.relationship('WeatherStation', back_populates='basin', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Basin {self.name}>'


class River(db.Model):
    """河流模型"""
    __tablename__ = 'rivers'
    river_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    length = db.Column(db.Float, nullable=False)
    basin_id = db.Column(db.Integer, db.ForeignKey('basins.basin_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    basin = db.relationship('Basin', back_populates='rivers')
    reservoirs = db.relationship('Reservoir', back_populates='river', cascade='all, delete-orphan')
    flood_control_facilities = db.relationship('FloodControlFacility', back_populates='river',
                                               cascade='all, delete-orphan')
    monitoring_stations = db.relationship('MonitoringStation', back_populates='river', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<River {self.name}>'


class Reservoir(db.Model):
    """水库模型"""
    __tablename__ = 'reservoirs'
    reservoir_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Float, nullable=False)
    river_id = db.Column(db.Integer, db.ForeignKey('rivers.river_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    river = db.relationship('River', back_populates='reservoirs')
    monitoring_stations = db.relationship('MonitoringStation', back_populates='reservoir', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Reservoir {self.name}>'


class FloodControlFacility(db.Model):
    """防洪设施模型"""
    __tablename__ = 'flood_control_facilities'
    facility_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    river_id = db.Column(db.Integer, db.ForeignKey('rivers.river_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    river = db.relationship('River', back_populates='flood_control_facilities')

    def __repr__(self):
        return f'<FloodControlFacility {self.name}>'


class WeatherStation(db.Model):
    """气象站模型"""
    __tablename__ = 'weather_stations'
    station_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    basin_id = db.Column(db.Integer, db.ForeignKey('basins.basin_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    basin = db.relationship('Basin', back_populates='weather_stations')

    def __repr__(self):
        return f'<WeatherStation {self.name}>'


class MonitoringStation(db.Model):
    """监测站模型"""
    __tablename__ = 'monitoring_stations'
    monitor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    river_id = db.Column(db.Integer, db.ForeignKey('rivers.river_id'), nullable=True)
    reservoir_id = db.Column(db.Integer, db.ForeignKey('reservoirs.reservoir_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系
    river = db.relationship('River', back_populates='monitoring_stations')
    reservoir = db.relationship('Reservoir', back_populates='monitoring_stations')

    def __repr__(self):
        return f'<MonitoringStation {self.name}>'


class PrecipitationData(db.Model):
    """降水数据模型（与气象站多对一关系）"""
    __tablename__ = 'precipitation_data'

    precipitation_id = db.Column(db.Integer, primary_key=True, comment='降水记录ID')
    station_id = db.Column(
        db.Integer,
        db.ForeignKey('weather_stations.station_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联气象站ID'
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True,
        comment='记录时间'
    )
    amount = db.Column(
        db.Numeric(6, 2),
        nullable=False,
        comment='降雨量(mm)'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系定义
    station = db.relationship(
        'WeatherStation',
        backref=db.backref('precipitation_data', lazy='dynamic', cascade='all, delete-orphan')
    )

    def __repr__(self):
        return f'<Precipitation {self.station.name} {self.timestamp}: {self.amount}mm>'


class WaterLevelData(db.Model):
    """水位数据模型（与监测站多对一关系）"""
    __tablename__ = 'water_level_data'

    water_level_id = db.Column(db.Integer, primary_key=True, comment='水位记录ID')
    monitor_id = db.Column(
        db.Integer,
        db.ForeignKey('monitoring_stations.monitor_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联监测站ID'
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    level = db.Column(db.Numeric(8, 3), nullable=False, comment='水位高程(m)')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系定义
    monitor = db.relationship(
        'MonitoringStation',
        backref=db.backref('water_level_data', lazy='dynamic')
    )

    # 水位警戒状态计算属性
    @property
    def alert_status(self):
        return self.level >= self.monitor.warning_level if self.monitor.warning_level else None


class FloodAlert(db.Model):
    """洪水警报系统"""
    __tablename__ = 'flood_alerts'

    alert_id = db.Column(db.Integer, primary_key=True, comment='警报ID')
    river_id = db.Column(
        db.Integer,
        db.ForeignKey('rivers.river_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联河流ID'
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True,
        comment='警报时间'
    )
    alert_level = db.Column(
        db.String(20),
        nullable=False,
        comment='警报级别(yellow/orange/red)'
    )
    description = db.Column(
        db.Text,
        comment='警报详细描述'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    # 关系定义
    river = db.relationship('River', backref=db.backref(
        'flood_alerts',
        lazy='dynamic',
        cascade='all, delete-orphan'
    ))

    # 约束条件
    __table_args__ = (
        db.CheckConstraint(
            "alert_level IN ('yellow', 'orange', 'red')",
            name='valid_alert_level'
        ),
    )

    def __repr__(self):
        return f'<FloodAlert {self.river.name} {self.alert_level}>'

    @property
    def is_red_alert(self):
        return self.alert_level == 'red'


class ReservoirReleaseData(db.Model):
    """水库放水记录"""
    __tablename__ = 'reservoir_releases'

    release_id = db.Column(db.Integer, primary_key=True, comment='放水记录ID')
    reservoir_id = db.Column(
        db.Integer,
        db.ForeignKey('reservoirs.reservoir_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联水库ID'
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True,
        comment='放水时间'
    )
    release_amount = db.Column(
        db.Numeric(10, 3),
        nullable=False,
        comment='放水量(万立方米)'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    reservoir = db.relationship('Reservoir', backref=db.backref(
        'release_records',
        lazy='dynamic',
        order_by='ReservoirReleaseData.timestamp.desc()'
    ))

    def __repr__(self):
        return f'<Release {self.reservoir.name} {self.timestamp}: {self.release_amount}>'


class RiverFlowData(db.Model):
    """河流流量实时监测"""
    __tablename__ = 'river_flow_data'

    flow_id = db.Column(db.Integer, primary_key=True, comment='流量记录ID')
    river_id = db.Column(
        db.Integer,
        db.ForeignKey('rivers.river_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联河流ID'
    )
    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        index=True,
        comment='记录时间'
    )
    flow_rate = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        comment='流量(m³/s)'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    river = db.relationship('River', backref=db.backref(
        'flow_data',
        lazy='dynamic',
        order_by='RiverFlowData.timestamp.desc()'
    ))

    def __repr__(self):
        return f'<FlowData {self.river.name} {self.flow_rate}m³/s>'


class HistoricalFloodData(db.Model):
    """历史洪水事件存档"""
    __tablename__ = 'historical_floods'

    flood_id = db.Column(db.Integer, primary_key=True, comment='洪水事件ID')
    river_id = db.Column(
        db.Integer,
        db.ForeignKey('rivers.river_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联河流ID'
    )
    start_time = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
        comment='洪水开始时间'
    )
    end_time = db.Column(
        db.DateTime,
        comment='洪水结束时间'
    )
    max_water_level = db.Column(
        db.Numeric(8, 3),
        nullable=False,
        comment='最高水位(m)'
    )
    affected_area = db.Column(
        db.Numeric(12, 2),
        comment='受灾面积(km²)'
    )

    river = db.relationship('River', backref=db.backref(
        'historical_floods',
        lazy='dynamic',
        order_by='HistoricalFloodData.start_time.desc()'
    ))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    __table_args__ = (
        db.CheckConstraint('start_time < end_time', name='valid_flood_period'),
    )

    @property
    def duration_days(self):
        if self.end_time:
            return (self.end_time - self.start_time).days
        return None


class ThresholdBase(db.Model):
    """阈值模型基类"""
    __abstract__ = True

    threshold_id = db.Column(db.Integer, primary_key=True)
    threshold_value = db.Column(db.Numeric(10, 3), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_exceeded(self, current_value):
        return float(current_value) > float(self.threshold_value)


class RainfallThreshold(ThresholdBase):
    """降雨量阈值"""
    __tablename__ = 'rainfall_thresholds'

    basin_id = db.Column(
        db.Integer,
        db.ForeignKey('basins.basin_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联流域ID'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    basin = db.relationship('Basin', backref=db.backref(
        'rainfall_thresholds',
        lazy='dynamic'
    ))


class WaterLevelThreshold(ThresholdBase):
    """水位阈值"""
    __tablename__ = 'water_level_thresholds'

    river_id = db.Column(
        db.Integer,
        db.ForeignKey('rivers.river_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联河流ID'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    river = db.relationship('River', backref=db.backref(
        'water_level_thresholds',
        lazy='dynamic'
    ))


class FloodControlStrategy(db.Model):
    """防洪应急预案"""
    __tablename__ = 'flood_control_strategies'

    strategy_id = db.Column(db.Integer, primary_key=True, comment='策略ID')
    river_id = db.Column(
        db.Integer,
        db.ForeignKey('rivers.river_id', ondelete='CASCADE'),
        nullable=False,
        comment='关联河流ID'
    )
    alert_level = db.Column(
        db.String(20),
        nullable=False,
        comment='触发警报级别'
    )
    action_plan = db.Column(
        db.Text,
        nullable=False,
        comment='应对措施'
    )
    contact_persons = db.Column(
        db.JSON,
        comment='联系人名单'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 新增字段

    river = db.relationship('River', backref=db.backref(
        'control_strategies',
        lazy='dynamic'
    ))

    __table_args__ = (
        db.UniqueConstraint('river_id', 'alert_level', name='uq_strategy'),
    )

