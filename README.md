# Myfirstrepositort

# 配置 Flask 应用
app = Flask(__name__)
app.config.from_pyfile('config.py')

# 初始化数据库
db = SQLAlchemy(app)