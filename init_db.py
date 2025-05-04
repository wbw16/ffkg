from app import create_app, db

app = create_app()
with app.app_context():
    # 清空并重建所有表
    db.drop_all()    # 删除所有现有表
    db.create_all()  # 创建所有定义的表
    print("数据库重建完成 ✅")
