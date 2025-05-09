from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, StringField,HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import DecimalField, DateTimeField
from wtforms.validators import DataRequired, NumberRange
from app.models import User
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

class ProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('当前密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[
        DataRequired(),
        Length(min=8, message='密码至少需要8个字符')
    ])
    confirm_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的密码必须一致')
    ])
class CreateUserForm(FlaskForm):
    id = HiddenField('ID')
    username = StringField('用户名', validators=[
        DataRequired(),
        Length(min=3, max=20, message='用户名长度3-20个字符')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(min=8, message='密码至少8位字符'),
        EqualTo('confirm_password', message='两次密码必须一致')
    ])
    confirm_password = PasswordField('确认密码')
    is_admin = BooleanField('管理员权限')
    submit = SubmitField('创建用户')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class UserForm(FlaskForm):
    id = HiddenField('ID')  # 添加这行
    username = StringField('用户名', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='两次输入的密码必须一致')
    ])
    confirm_password = PasswordField('确认密码')
    is_admin = BooleanField('管理员')
    active = BooleanField('激活状态', default=True)
    submit = SubmitField('保存')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and (not hasattr(self, 'id') or (hasattr(self, 'id') and user.id != self.id.data)):
            raise ValidationError('该用户名已被使用')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and (not hasattr(self, 'id') or (hasattr(self, 'id') and user.id != self.id.data)):
            raise ValidationError('该邮箱已被使用')

class AlertForm(FlaskForm):
    river_id = SelectField(
        '关联河流',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    alert_level = SelectField(
        '警报级别',
        choices=[('yellow', '黄色预警'), ('orange', '橙色预警'), ('red', '红色预警')],
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    description = TextAreaField(
        '警报描述',
        validators=[DataRequired(), Length(max=500)],
        render_kw={"class": "form-control", "rows": 4}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import River
        self.river_id.choices = [(r.river_id, r.name) for r in River.query.all()]

class ReleaseForm(FlaskForm):
    reservoir_id = SelectField(
        '水库名称',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    amount = DecimalField(
        '放水量 (万立方米)',
        validators=[
            DataRequired(),
            NumberRange(min=0.1, message='必须大于0.1万立方米')
        ],
        places=2,
        render_kw={"class": "form-control"}
    )
    timestamp = DateTimeField(
        '放水时间',
        format='%Y-%m-%d %H:%M',
        render_kw={
            "class": "form-control datetimepicker",
            "placeholder": "YYYY-MM-DD HH:MM"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Reservoir
        self.reservoir_id.choices = [
            (r.reservoir_id, r.name)
            for r in Reservoir.query.order_by(Reservoir.name).all()
        ]

class PrecipitationForm(FlaskForm):
    station_id = SelectField(
        '气象站',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    amount = DecimalField(
        '降水量 (mm)',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=1000, message='必须在0-1000mm之间')
        ],
        places=1,
        render_kw={
            "class": "form-control",
            "step": "0.1"
        }
    )
    timestamp = DateTimeField(
        '记录时间',
        format='%Y-%m-%d %H:%M',
        render_kw={
            "class": "form-control datetimepicker-input",
            "data-toggle": "datetimepicker",
            "data-target": "#timestamp"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import WeatherStation
        self.station_id.choices = [
            (s.station_id, f"{s.name} ({s.code})")
            for s in WeatherStation.query.order_by(WeatherStation.name).all()
        ]
class WaterLevelForm(FlaskForm):
    monitor_id = SelectField(
        '监测站',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"},
        description="选择水位监测站点"
    )
    level = DecimalField(
        '水位高程 (m)',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=1000, message='有效范围0-1000米')
        ],
        places=3,
        render_kw={
            "class": "form-control",
            "step": "0.001",
            "placeholder": "精确到毫米级"
        }
    )
    timestamp = DateTimeField(
        '记录时间',
        validators=[DataRequired()],
        format='%Y-%m-%d %H:%M',
        render_kw={
            "class": "form-control datetimepicker-input",
            "data-toggle": "datetimepicker"
        }
    )
    notes = TextAreaField(
        '备注',
        validators=[Length(max=200)],
        render_kw={
            "class": "form-control",
            "rows": 2,
            "placeholder": "可记录特殊情况说明"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import MonitoringStation
        self.monitor_id.choices = [
            (m.monitor_id, f"{m.name} ({m.river.name})")
            for m in MonitoringStation.query.order_by(MonitoringStation.name).all()
        ]


class RiverFlowForm(FlaskForm):
    river_id = SelectField(
        '选择河流*',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    flow_rate = DecimalField(
        '流量值 (m³/s)*',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="流量值不能为负数")
        ],
        places=2,
        render_kw={
            "class": "form-control",
            "placeholder": "请输入流量数值",
            "step": "0.01"
        }
    )
    timestamp = DateTimeField(
        '记录时间',
        format='%Y-%m-%d %H:%M',
        render_kw={
            "class": "form-control datetimepicker-input",
            "data-toggle": "datetimepicker"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import River
        self.river_id.choices = [
            (r.river_id, f"{r.name} - {r.basin.name}流域")
            for r in River.query.order_by(River.name).all()
        ]

    def validate_timestamp(self, field):
        if field.data and field.data > datetime.utcnow():
            raise ValidationError('记录时间不能晚于当前时间')


class HistoricalFloodForm(FlaskForm):
    river_id = SelectField(
        '关联河流',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    start_time = DateTimeField(
        '开始时间',
        format='%Y-%m-%d %H:%M',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control datetimepicker-input",
            "data-toggle": "datetimepicker"
        }
    )
    end_time = DateTimeField(
        '结束时间',
        format='%Y-%m-%d %H:%M',
        render_kw={
            "class": "form-control datetimepicker-input",
            "data-toggle": "datetimepicker"
        }
    )
    max_water_level = DecimalField(
        '最高水位(m)',
        validators=[DataRequired(), NumberRange(min=0)],
        places=3,
        render_kw={"class": "form-control"}
    )
    affected_area = DecimalField(
        '受灾面积(km²)',
        places=2,
        render_kw={"class": "form-control"}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import River
        self.river_id.choices = [
            (r.river_id, r.name) for r in River.query.order_by(River.name).all()
        ]

    def validate(self):
        if not super().validate():
            return False

        # 验证结束时间必须晚于开始时间
        if self.end_time.data and self.end_time.data <= self.start_time.data:
            self.end_time.errors.append('结束时间必须晚于开始时间')
            return False

        return True

class ThresholdForm(FlaskForm):
    threshold_value = DecimalField(
        '阈值数值',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="必须为正数")
        ],
        places=3,
        render_kw={
            "class": "form-control",
            "placeholder": "请输入具体阈值数值"
        }
    )
    description = TextAreaField(
        '描述说明',
        validators=[Length(max=500)],
        render_kw={
            "class": "form-control",
            "rows": 4,
            "placeholder": "可填写阈值用途、计算依据等"
        }
    )


class RainfallThresholdForm(FlaskForm):
    basin_id = SelectField(
        '所属流域',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    threshold_value = DecimalField(
        '阈值(mm)',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="必须为正数")
        ],
        places=2,
        render_kw={
            "class": "form-control",
            "placeholder": "请输入降雨量阈值"
        }
    )
    description = TextAreaField(
        '阈值说明',
        validators=[Length(max=500)],
        render_kw={
            "class": "form-control",
            "rows": 4,
            "placeholder": "请说明阈值适用条件和依据"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Basin
        self.basin_id.choices = [
            (b.basin_id, f"{b.name} ({b.region})")
            for b in Basin.query.order_by(Basin.name).all()
        ]


class WaterLevelThresholdForm(FlaskForm):
    river_id = SelectField(
        '关联河流',
        coerce=int,
        validators=[DataRequired()],
        render_kw={
            "class": "form-select",
            "data-live-search": "true"
        }
    )
    threshold_value = DecimalField(
        '阈值水位(m)',
        validators=[
            DataRequired(),
            NumberRange(min=0, message="必须为正数")
        ],
        places=3,
        render_kw={
            "class": "form-control",
            "placeholder": "请输入水位阈值",
            "step": "0.001"
        }
    )
    description = TextAreaField(
        '阈值说明',
        validators=[Length(max=500)],
        render_kw={
            "class": "form-control",
            "rows": 3,
            "placeholder": "请说明水位阈值用途及依据"
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import River
        self.river_id.choices = [
            (r.river_id, f"{r.name} (长度: {r.length}km)")
            for r in River.query.order_by(River.name).all()
        ]
class FloodControlStrategyForm(FlaskForm):
    river_id = SelectField(
        '关联河流*',
        coerce=int,
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    alert_level = SelectField(
        '警报级别*',
        choices=[
            ('yellow', '黄色警报 (Ⅲ级)'),
            ('orange', '橙色警报 (Ⅱ级)'),
            ('red', '红色警报 (Ⅰ级)')
        ],
        validators=[DataRequired()],
        render_kw={"class": "form-select"}
    )
    action_plan = TextAreaField(
        '应急预案*',
        validators=[DataRequired(), Length(min=10)],
        render_kw={
            "class": "form-control",
            "rows": 8,
            "placeholder": "详细描述应急响应流程、物资调配方案等..."
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import River
        self.river_id.choices = [
            (r.river_id, f"{r.name} - {r.basin.name}流域")
            for r in River.query.order_by(River.name).all()
        ]

def generate_contact_field(index, contact=None):
    """生成联系人表单字段模板"""
    return {
        'name': f'contact_name_{index}',
        'phone': f'contact_phone_{index}',
        'name_value': contact['name'] if contact and len(contact) > index-1 else '',
        'phone_value': contact['phone'] if contact and len(contact) > index-1 else ''
    }
