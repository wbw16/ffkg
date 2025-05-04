# 在 app/__init__.py 或 commands.py 中添加
# app/commands.py
import click
from app.neo4j_models import Neo4jSync
from app.extensions import db

def register_commands(app):
    @app.cli.command()
    def sync_neo4j():
        """同步数据到 Neo 知识图谱"""
        click.echo("开始同步数据到 Neo4j...")
        Neo4jSync.sync_all()
        click.echo("数据同步完成")