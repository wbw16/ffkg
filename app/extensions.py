#app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_redis import FlaskRedis
from py2neo import Graph
from config import Config


db = SQLAlchemy()
login_manager = LoginManager()
#extensions.py
redis_client = FlaskRedis()

neo4j_graph = Graph(Config.NEO4J_URI, auth=Config.NEO4J_AUTH)