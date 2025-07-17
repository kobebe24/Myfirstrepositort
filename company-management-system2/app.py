from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, config
from flask.cli import load_dotenv
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import datetime
import psutil
import platform
import subprocess
import importlib.util
import os
from config import config
from extensions import db
from routes import main_bp, department_bp, member_bp, comment_bp, user_bp, operation_bp, log_bp, system_bp
from flask_wtf import FlaskForm  # 假设使用 Flask-WTF 来创建表单
from wtforms import StringField, PasswordField  # 导入表单字段
from wtforms.validators import DataRequired
from models import User
# 定义登录表单类
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

# 加载环境变量
load_dotenv()

# 配置 Flask 应用
app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])
app.config.from_pyfile('config.py')

db.init_app(app)  # 在 Flask 应用中注册 SQLAlchemy 实例
# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
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
# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/users')  # 注册用户蓝图，所有路由前缀为 /users
app.register_blueprint(main_bp, url_prefix='/')      # 注册主蓝图
app.register_blueprint(department_bp, url_prefix='/departments')
app.register_blueprint(member_bp, url_prefix='/members')
app.register_blueprint(comment_bp, url_prefix='/comments')
app.register_blueprint(operation_bp, url_prefix='/operations')
app.register_blueprint(log_bp, url_prefix='/logs')
app.register_blueprint(system_bp, url_prefix='/system')



# 导入模型
from models import (
    Department, Member, Comment, User, Announcement, Ad,
    LoginLog, OperationLog, ErrorLog, SystemInfo
)

# 定义用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 记录操作日志函数
def log_operation(content):
    operation_log = OperationLog(
        user_id=current_user.id,
        operation_type='system',
        operation_content=content,
        operation_time=datetime.utcnow()
    )
    db.session.add(operation_log)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()


# 获取系统信息函数
def get_system_info():
    system = {
        'system_name': '公司部门管理系统',
        'version': '1.0.0',
        'os': platform.system(),
        'system_platform': platform.platform(),
        'hostname': platform.node(),
        'ip_address': '127.0.0.1',  # 可根据实际情况获取
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': platform.python_version()
    }
    cpu = {
        'cpu_count': psutil.cpu_count(logical=False),
        'cpu_count_logical': psutil.cpu_count(logical=True),
        'cpu_freq': psutil.cpu_freq().current,
        'cpu_percent': psutil.cpu_percent()
    }
    memory = {
        'total_memory': round(psutil.virtual_memory().total / (1024 ** 3), 2),
        'available_memory': round(psutil.virtual_memory().available / (1024 ** 3), 2),
        'memory_percent': psutil.virtual_memory().percent
    }
    disk = {
        'total_disk': round(psutil.disk_usage('/').total / (1024 ** 3), 2),
        'used_disk': round(psutil.disk_usage('/').used / (1024 ** 3), 2),
        'free_disk': round(psutil.disk_usage('/').free / (1024 ** 3), 2),
        'disk_percent': psutil.disk_usage('/').percent
    }
    try:
        mysql_version = subprocess.check_output(['mysql', '--version']).decode('utf-8').strip()
    except Exception:
        mysql_version = '未安装'
    try:
        nginx_version = subprocess.check_output(['nginx', '-v'], stderr=subprocess.STDOUT).decode('utf-8').strip()
    except Exception:
        nginx_version = '未安装'
    flask_version = importlib.util.find_spec('flask').loader.load_module().__version__
    sqlalchemy_version = importlib.util.find_spec('sqlalchemy').loader.load_module().__version__

    return {
        'system': system,
        'cpu': cpu,
        'memory': memory,
        'disk': disk,
        'mysql_version': mysql_version,
        'nginx_version': nginx_version,
        'flask_version': flask_version,
        'sqlalchemy_version': sqlalchemy_version
    }

# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 创建表单实例
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            # 记录登录日志
            login_log = LoginLog(
                user_id=user.id,
                ip_address=request.remote_addr,
                login_time=datetime.utcnow()
            )
            db.session.add(login_log)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'error')
    return render_template('login.html', form=form)  # 传递表单实例到模板

# 注销路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 启动时自动创建表
    app.run(debug=app.config['DEBUG'])
