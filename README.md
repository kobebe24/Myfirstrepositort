
# 配置 Flask 应用
app = Flask(__name__)
app.config.from_pyfile('config.py')

# 初始化数据库
db = SQLAlchemy(app)

# 数据库用户：root   密码：admin123

# 初始化管理员账号：admin   密码：admin123