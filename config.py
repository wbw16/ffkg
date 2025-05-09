import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.flaskenv'))


class Config:
    # MySQL 配置
    DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'wbw')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_NAME = os.getenv('DB_NAME', 'ffkg')

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@'
        f'{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

    REDIS_URL = (
        f'redis://{f":{REDIS_PASSWORD}@" if REDIS_PASSWORD else ""}'
        f'{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
    )

    # Neo4j 配置
    NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
    NEO4J_PORT = int(os.getenv('NEO4J_PORT', 7687))
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '12345678')

    NEO4J_URI = f"bolt://{NEO4J_HOST}:{NEO4J_PORT}"
    NEO4J_AUTH = (NEO4J_USER, NEO4J_PASSWORD)

    # DeepSeek API配置 (通过本地Dify部署)
    DEEPSEEK_API_BASE = 'http://127.0.0.1/v1'  # 本地Dify地址
    DEEPSEEK_API_KEY = 'app-ZplO6IpcY82YRTbHTJ0llmt4'

    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    SESSION_TYPE = 'redis'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
