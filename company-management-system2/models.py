from flask_sqlalchemy import SQLAlchemy
from extensions import db  # 从 app.py 导入 db 实例
from datetime import datetime

# 部门模型
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    manager = db.relationship('User', backref='managed_departments', foreign_keys=[manager_id])
    members = db.relationship('Member', backref='department', lazy=True)


# 成员模型
class Member(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    position = db.Column(db.String(100))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


# 评论模型
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    user = db.relationship('User', backref='comments')


# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user'), default='user')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    login_logs = db.relationship('LoginLog', backref='user', lazy=True)
    operation_logs = db.relationship('OperationLog', backref='user', lazy=True)

    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    # 添加 is_active 属性
    @property
    def is_active(self):
        return True

    # 以下是 Flask-Login 还需要的其他属性和方法，建议一并添加
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# 通知公告模型
class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系定义
    creator = db.relationship('User', backref='announcements')

# 广告管理模型
class Ad(db.Model):
    __tablename__ = 'ads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 确保此字段存在
    image_url = db.Column(db.String(255))
    link = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    create_time = db.Column(db.DateTime, default=datetime.utcnow)



# 登录日志模型
class LoginLog(db.Model):
    __tablename__ = 'login_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)


# 操作日志模型
class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    operation_type = db.Column(db.String(100), nullable=False)
    operation_content = db.Column(db.Text)
    operation_time = db.Column(db.DateTime, default=datetime.utcnow)


# 错误日志模型
class ErrorLog(db.Model):
    __tablename__ = 'error_logs'
    id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# 系统信息模型
class SystemInfo(db.Model):
    __tablename__ = 'system_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255))
    update_time = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
