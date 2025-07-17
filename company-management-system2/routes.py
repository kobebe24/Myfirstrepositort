from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime
import psutil
import socket
import platform
import subprocess
import importlib.util
import os
from models import Department
# 导入模型
from models import (
    db, Department, Member, Comment, User, Announcement, Ad,
    LoginLog, OperationLog, ErrorLog, SystemInfo
)

# 创建蓝图
main_bp = Blueprint('main', __name__)
department_bp = Blueprint('department', __name__, url_prefix='/departments')
member_bp = Blueprint('member', __name__, url_prefix='/members')
comment_bp = Blueprint('comment', __name__, url_prefix='/comments')
user_bp = Blueprint('user', __name__, url_prefix='/users')
operation_bp = Blueprint('operation', __name__, url_prefix='/operations')
log_bp = Blueprint('log', __name__, url_prefix='/logs')
system_bp = Blueprint('system', __name__, url_prefix='/system')


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


# 记录操作日志函数
def log_operation(content):
    operation_log = OperationLog(
        user_id=current_user.id,
        operation_type='system',
        operation_content=content,
        operation_time=datetime.utcnow()
    )
    db.session.add(operation_log)
    db.session.commit()


# 主路由 - 总览页面
@main_bp.route('/')
@login_required
def index():
    # 统计信息
    department_count = Department.query.count()
    member_count = Member.query.count()
    user_count = User.query.count()
    announcement_count = Announcement.query.count()

    # 最新公告
    latest_announcements = Announcement.query.order_by(Announcement.create_time.desc()).limit(5).all()

    # 系统信息
    system_info = get_system_info()

    return render_template('index.html',
                           department_count=department_count,
                           member_count=member_count,
                           user_count=user_count,
                           announcement_count=announcement_count,
                           announcements=latest_announcements,
                           system_info=system_info)


# 部门管理路由
@department_bp.route('/')
@login_required
def list_departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)

@department_bp.route('/add', methods=['POST'])
@login_required
def add_department():
    name = request.form.get('name')
    manager_id = request.form.get('manager_id') or None

    if not name:
        flash('部门名称不能为空', 'error')
        return redirect(url_for('department.list_departments'))

    department = Department(name=name, manager_id=manager_id)
    db.session.add(department)
    try:
        db.session.commit()
        # 记录操作日志
        log_operation(f"创建部门: {name}")
        flash('部门创建成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'部门创建失败: {str(e)}', 'error')

    return redirect(url_for('department.list_departments'))

@department_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_department(id):
    department = Department.query.get_or_404(id)

    # 检查是否有成员
    if department.members:
        flash('该部门下有成员，无法删除', 'error')
        return redirect(url_for('department.list_departments'))

    try:
        db.session.delete(department)
        db.session.commit()
        # 记录操作日志
        log_operation(f"删除部门: {department.name}")
        flash('部门删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'部门删除失败: {str(e)}', 'error')

    return redirect(url_for('department.list_departments'))

# 添加编辑部门路由
@department_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_department(id):
    department = Department.query.get_or_404(id)
    name = request.form.get('name')
    manager_id = request.form.get('manager_id') or None

    if not name:
        flash('部门名称不能为空', 'error')
        return redirect(url_for('department.list_departments'))

    department.name = name
    department.manager_id = manager_id

    try:
        db.session.commit()
        # 记录操作日志
        log_operation(f"编辑部门: {name}")
        flash('部门编辑成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'部门编辑失败: {str(e)}', 'error')

    return redirect(url_for('department.list_departments'))


# 成员管理路由
@member_bp.route('/')
@login_required
def list_members():
    members = Member.query.all()
    departments = Department.query.all()
    return render_template('members.html', members=members, departments=departments)

@member_bp.route('/add', methods=['POST'])
@login_required
def add_member():
    name = request.form.get('name')
    email = request.form.get('email')
    department_id = request.form.get('department_id')
    position = request.form.get('position')

    if not name or not email or not department_id:
        flash('姓名、邮箱和部门不能为空', 'error')
        return redirect(url_for('member.list_members'))

    # 检查邮箱是否已存在
    if Member.query.filter_by(email=email).first():
        flash('该邮箱已被使用', 'error')
        return redirect(url_for('member.list_members'))

    member = Member(
        name=name,
        email=email,
        department_id=department_id,
        position=position
    )

    db.session.add(member)
    try:
        db.session.commit()
        log_operation(f"添加成员: {name}")
        flash('成员添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'成员添加失败: {str(e)}', 'error')

    return redirect(url_for('member.list_members'))

@member_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_member(id):
    member = Member.query.get_or_404(id)
    try:
        db.session.delete(member)
        db.session.commit()
        log_operation(f"删除成员: {member.name}")
        flash('成员删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'成员删除失败: {str(e)}', 'error')

    return redirect(url_for('member.list_members'))

# 添加编辑成员路由
@member_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_member(id):
    member = Member.query.get_or_404(id)
    name = request.form.get('name')
    email = request.form.get('email')
    department_id = request.form.get('department_id')
    position = request.form.get('position')

    if not name or not email or not department_id:
        flash('姓名、邮箱和部门不能为空', 'error')
        return redirect(url_for('member.list_members'))

    existing_member = Member.query.filter(
        Member.email == email,
        Member.id != id
    ).first()
    if existing_member:
        flash('该邮箱已被其他成员使用', 'error')
        return redirect(url_for('member.list_members'))

    member.name = name
    member.email = email
    member.department_id = department_id
    member.position = position

    try:
        db.session.commit()
        log_operation(f"编辑成员: {name}")
        flash('成员信息更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'更新失败: {str(e)}', 'error')

    return redirect(url_for('member.list_members'))


# 评论管理路由
@comment_bp.route('/')
@login_required
def list_comments():
    comments = Comment.query.all()
    return render_template('comments.html', comments=comments)


@comment_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    try:
        db.session.delete(comment)
        db.session.commit()
        # 记录操作日志
        log_operation(f"删除评论: ID={id}")
        flash('评论删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'评论删除失败: {str(e)}', 'error')

    return redirect(url_for('comment.list_comments'))


# 用户管理路由
@user_bp.route('/')
@login_required
def list_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@user_bp.route('/add', methods=['POST'])
@login_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username or not password:
        flash('用户名和密码不能为空', 'error')
        return redirect(url_for('user.list_users'))

    user = User(username=username, role=role)
    user.set_password(password)

    db.session.add(user)
    try:
        db.session.commit()
        log_operation(f"添加用户: {username}")
        flash('用户添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'用户添加失败: {str(e)}', 'error')

    return redirect(url_for('user.list_users'))

@user_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    user = User.query.get_or_404(id)
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    if not username:
        flash('用户名不能为空', 'error')
        return redirect(url_for('user.list_users'))

    user.username = username
    user.role = role

    if password:
        user.set_password(password)

    try:
        db.session.commit()
        log_operation(f"编辑用户: {username}")
        flash('用户信息更新成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'用户信息更新失败: {str(e)}', 'error')

    return redirect(url_for('user.list_users'))

@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('不能删除当前登录用户', 'error')
        return redirect(url_for('user.list_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        log_operation(f"删除用户: {user.username}")
        flash('用户删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'用户删除失败: {str(e)}', 'error')

    return redirect(url_for('user.list_users'))




# 通知公告列表
@operation_bp.route('/announcements')
@login_required
def list_announcements():
    announcements = Announcement.query.order_by(Announcement.create_time.desc()).all()
    return render_template('announcements.html', announcements=announcements)


# 添加公告
@operation_bp.route('/add_announcement', methods=['POST'])
@login_required
def add_announcement():
    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        flash('标题和内容不能为空', 'error')
        return redirect(url_for('operation.list_announcements'))

    announcement = Announcement(
        title=title,
        content=content,
        creator_id=current_user.id,
        create_time=datetime.utcnow()
    )

    db.session.add(announcement)
    try:
        db.session.commit()
        log_operation(f"添加公告: {title}")
        flash('公告添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'公告添加失败: {str(e)}', 'error')

    return redirect(url_for('operation.list_announcements'))


# 编辑公告
@operation_bp.route('/edit_announcement/<int:id>', methods=['POST'])
@login_required
def edit_announcement(id):
    announcement = Announcement.query.get_or_404(id)
    title = request.form.get('title')
    content = request.form.get('content')

    if not title or not content:
        flash('标题和内容不能为空', 'error')
        return redirect(url_for('operation.list_announcements'))

    announcement.title = title
    announcement.content = content
    announcement.update_time = datetime.utcnow()

    try:
        db.session.commit()
        log_operation(f"编辑公告: {title}")
        flash('公告编辑成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'公告编辑失败: {str(e)}', 'error')

    return redirect(url_for('operation.list_announcements'))


# 删除公告
@operation_bp.route('/delete_announcement/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    announcement = Announcement.query.get_or_404(id)

    try:
        db.session.delete(announcement)
        db.session.commit()
        log_operation(f"删除公告: {announcement.title}")
        flash('公告删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'公告删除失败: {str(e)}', 'error')

    return redirect(url_for('operation.list_announcements'))

#登录日志管理路由
@log_bp.route('/login_logs')
@login_required
def list_login_logs():
    login_logs = LoginLog.query.all()
    return render_template('LoginLog.html', login_logs=login_logs)

# 操作日志管理路由
@log_bp.route('/operation_logs')
@login_required
def list_operation_logs():
    operation_logs = OperationLog.query.all()
    return render_template('OperationLog.html', operation_logs=operation_logs)


@log_bp.route('/list_error_logs')
@login_required
def list_error_logs():
    error_logs = ErrorLog.query.all()
    return render_template('ErrorLog.html', error_logs=error_logs)