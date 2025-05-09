# 在 app/__init__.py 或 commands.py 中添加
# app/commands.py
import click
from app.neo4j_models import Neo4jSync
from flask.cli import with_appcontext
from app.models import User
from app.extensions import db


@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@click.option('--email', help='Admin email address')
@with_appcontext
def create_admin(username, password, email=None):
    """创建管理员账号"""
    if not email:
        email = f"{username}@example.com"  # 默认邮箱

    try:
        if User.query.filter_by(username=username).first():
            click.echo(f"错误：用户名 {username} 已存在", err=True)
            return

        if User.query.filter_by(email=email).first():
            click.echo(f"错误：邮箱 {email} 已被使用", err=True)
            return

        admin = User(username=username, email=email, is_admin=True)
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        click.echo(f"管理员 {username} 创建成功")

    except Exception as e:
        db.session.rollback()
        click.echo(f"创建管理员时出错: {str(e)}", err=True)


def register_commands(app):
    @app.cli.command()
    def sync_neo4j():
        """同步数据到 Neo 知识图谱"""
        click.echo("开始同步数据到 Neo4j...")
        Neo4jSync.sync_all()
        click.echo("数据同步完成")