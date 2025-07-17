from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask.cli import load_dotenv
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from datetime import datetime
import psutil
import platform
import subprocess
import importlib.util
import os
import socket
from config import config
from extensions import db
from routes import main_bp, department_bp, member_bp, comment_bp, user_bp, operation_bp, log_bp, system_bp
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from models import User, OperationLog, LoginLog


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

# 尝试从 config.py 加载配置，如果文件存在
config_path = 'config.py'
if os.path.exists(config_path):
    app.config.from_pyfile(config_path)
else:
    print(f"警告: 配置文件 {config_path} 不存在")

# 初始化数据库
db.init_app(app)

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/users')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(department_bp, url_prefix='/departments')
app.register_blueprint(member_bp, url_prefix='/members')
app.register_blueprint(comment_bp, url_prefix='/comments')
app.register_blueprint(operation_bp, url_prefix='/operations')
app.register_blueprint(log_bp, url_prefix='/logs')
app.register_blueprint(system_bp, url_prefix='/system')


# 定义用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 记录操作日志函数
def log_operation(content):
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None  # 对于未认证用户

    operation_log = OperationLog(
        user_id=user_id,
        operation_type='system',
        operation_content=content,
        operation_time=datetime.utcnow()
    )
    db.session.add(operation_log)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"操作日志记录失败: {str(e)}")


# 获取系统信息函数
def get_system_info():
    system = {
        'system_name': '公司部门管理系统',
        'version': '1.0.0',
        'os': platform.system(),
        'system_platform': platform.platform(),
        'hostname': platform.node(),
        'ip_address': '127.0.0.1',
        'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'python_version': platform.python_version()
    }

    # 获取CPU信息
    try:
        cpu = {
            'cpu_count': psutil.cpu_count(logical=False),
            'cpu_count_logical': psutil.cpu_count(logical=True),
            'cpu_percent': psutil.cpu_percent()
        }
        if hasattr(psutil, 'cpu_freq') and psutil.cpu_freq():
            cpu['cpu_freq'] = psutil.cpu_freq().current
    except Exception as e:
        print(f"获取CPU信息失败: {e}")
        cpu = {}

    # 获取内存信息
    try:
        mem = psutil.virtual_memory()
        memory = {
            'total_memory': round(mem.total / (1024 ** 3), 2),
            'available_memory': round(mem.available / (1024 ** 3), 2),
            'memory_percent': mem.percent
        }
    except Exception as e:
        print(f"获取内存信息失败: {e}")
        memory = {}

    # 获取磁盘信息
    try:
        disk = psutil.disk_usage('/')
        disk_info = {
            'total_disk': round(disk.total / (1024 ** 3), 2),
            'used_disk': round(disk.used / (1024 ** 3), 2),
            'free_disk': round(disk.free / (1024 ** 3), 2),
            'disk_percent': disk.percent
        }
    except Exception as e:
        print(f"获取磁盘信息失败: {e}")
        disk_info = {}

    # 获取软件版本
    software_versions = {}
    try:
        mysql_version = subprocess.check_output(['mysql', '--version']).decode('utf-8').strip()
        software_versions['mysql_version'] = mysql_version
    except Exception:
        software_versions['mysql_version'] = '未安装'

    try:
        nginx_version = subprocess.check_output(['nginx', '-v'], stderr=subprocess.STDOUT).decode('utf-8').strip()
        software_versions['nginx_version'] = nginx_version
    except Exception:
        software_versions['nginx_version'] = '未安装'

    try:
        import flask
        software_versions['flask_version'] = flask.__version__
    except ImportError:
        software_versions['flask_version'] = '未安装'

    try:
        import sqlalchemy
        software_versions['sqlalchemy_version'] = sqlalchemy.__version__
    except ImportError:
        software_versions['sqlalchemy_version'] = '未安装'

    return {
        'system': system,
        'cpu': cpu,
        'memory': memory,
        'disk': disk_info,
        'software': software_versions
    }


# 登录路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            # 记录登录日志
            try:
                login_log = LoginLog(
                    user_id=user.id,
                    ip_address=request.remote_addr,
                    login_time=datetime.utcnow()
                )
                db.session.add(login_log)
                db.session.commit()
            except Exception as e:
                print(f"登录日志记录失败: {str(e)}")
                db.session.rollback()

            return redirect(url_for('main.index'))
        else:
            flash('用户名或密码错误', 'error')
    return render_template('login.html', form=form)


# 注销路由
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    # 获取本机IP地址
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        print(f"获取IP地址失败: {e}")
        local_ip = '127.0.0.1'

    print(f"服务器将运行在: http://{local_ip}:5000")
    print("请确保防火墙已开放5000端口")

    # 在应用上下文中执行数据库操作
    with app.app_context():
        try:
            # 创建所有表
            db.create_all()
            print("数据库表创建成功")

            # 尝试创建管理员账号（如果不存在）
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    role='admin',
                    email='admin@example.com'  # 添加必需的字段
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                print('管理员账号创建成功')
            else:
                print('管理员账号已存在')

        except Exception as e:
            print(f"数据库初始化失败: {str(e)}")
            # 打印数据库URI用于调试（注意：生产环境不要这样做）
            print(f"数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))