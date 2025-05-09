from flask import Flask
from flask_login import LoginManager
from app.commands import register_commands
from config import Config
from app.extensions import db, login_manager, redis_client
from app.routes.main import main_bp
from app.routes.basins import basins_bp
from app.routes.rivers import rivers_bp
from app.routes.reservoirs import reservoirs_bp
from app.routes.facilities import facilities_bp
from app.routes.stations import stations_bp
from app.routes.monitors import monitors_bp
from app.routes.alerts import alert_bp
from app.routes.precipitation import precip_bp
from app.routes.reservoir_release import release_bp
from app.routes.riverflow import river_flow_bp
from app.routes.waterlevel import water_bp
from app.routes.historicalflood import flood_bp
from app.routes.threshold import threshold_bp
from app.routes.rainfallthreshold import rainfall_threshold_bp
from app.routes.waterlevelthreshold import water_level_threshold_bp
from app.routes.floodcontrol import flood_control_bp
from app.routes.neo4j import neo4j_bp
from app.routes.auth import auth_bp
from app.routes.admin import admin_bp
from app.routes.status import status_bp
from app.routes.chat import chat_bp
from app.models import User  # Assuming you'll create a User model
from app.commands import create_admin


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    redis_client.init_app(app)
    login_manager.init_app(app)

    # Login manager configuration
    login_manager.login_view = 'auth.login'  # You'll need to create this route
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(basins_bp)
    app.register_blueprint(rivers_bp)
    app.register_blueprint(reservoirs_bp)
    app.register_blueprint(facilities_bp)
    app.register_blueprint(stations_bp)
    app.register_blueprint(monitors_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(precip_bp)
    app.register_blueprint(release_bp)
    app.register_blueprint(river_flow_bp)
    app.register_blueprint(water_bp)
    app.register_blueprint(flood_bp)
    app.register_blueprint(threshold_bp)
    app.register_blueprint(flood_control_bp)
    app.register_blueprint(rainfall_threshold_bp)
    app.register_blueprint(water_level_threshold_bp)
    app.register_blueprint(neo4j_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(chat_bp)
    # Create database tables
    with app.app_context():
        db.create_all()

    register_commands(app)
    app.cli.add_command(create_admin)

    return app
