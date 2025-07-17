from app import app, db
from models import User

# 初始化 Flask 应用上下文
with app.app_context():
    # 创建一个新的管理员用户
    admin_user = User(
        username='admin',
        role='admin'
    )
    # 设置密码
    admin_user.set_password('admin123')
    # 将用户添加到数据库会话
    db.session.add(admin_user)
    # 提交会话以保存更改
    try:
        db.session.commit()
        print('管理员账号创建成功')
    except Exception as e:
        db.session.rollback()
        print(f'管理员账号创建失败: {str(e)}')
