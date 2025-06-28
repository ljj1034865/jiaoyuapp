from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import date
import pymysql
from flask_cors import CORS

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = 'your_strong_secret_key_here'
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ljj03241108@localhost/tutoring_system'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
db = SQLAlchemy(app)

# 数据模型
class TutoringJobs(db.Model):
    __tablename__ = 'tutoring_jobs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    district = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(50), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    salary = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)

class AdminUsers(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# 前端路由
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/list')
def list_page():
    return render_template('list.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# API路由
@app.route('/api/check_login', methods=['GET'])
def check_login():
    if 'admin_id' in session:
        admin = AdminUsers.query.get(session['admin_id'])
        if admin:
            return jsonify({
                'logged_in': True, 
                'admin_id': session['admin_id'],
                'username': admin.username
            })
    return jsonify({'logged_in': False})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': '缺少请求数据'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
    
    admin = AdminUsers.query.filter_by(username=username, password=password).first()
    
    if admin:
        session['admin_id'] = admin.id
        return jsonify({
            'success': True,
            'admin_id': admin.id,
            'username': admin.username
        })
    
    return jsonify({'success': False, 'message': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    if 'admin_id' in session:
        session.pop('admin_id', None)
    return jsonify({'success': True})

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    try:
        district = request.args.get('district', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if district == 'all':
            query = TutoringJobs.query.order_by(TutoringJobs.date.desc())
        else:
            query = TutoringJobs.query.filter_by(district=district).order_by(TutoringJobs.date.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        jobs = pagination.items
        
        job_list = []
        for job in jobs:
            job_dict = {
                'id': job.id,
                'district': job.district,
                'title': job.title,
                'category': job.category,
                'subject': job.subject,
                'grade': job.grade,
                'requirements': job.requirements,
                'salary': job.salary,
                'contact': job.contact,
                'date': job.date.strftime('%Y-%m-%d'),
                'location': job.location,
                'details': job.details
            }
            job_list.append(job_dict)
        
        return jsonify({
            'success': True,
            'jobs': job_list,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs', methods=['POST'])
def create_job():
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': '请先登录管理员账号'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '缺少请求数据'}), 400
    
    required_fields = ['title', 'district', 'category', 'grade', 'subject', 'salary', 'location', 'requirements', 'contact', 'details']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'字段 "{field}" 不能为空'}), 400
    
    try:
        new_job = TutoringJobs(
            title=data['title'],
            district=data['district'],
            category=data['category'],
            grade=data['grade'],
            subject=data['subject'],
            salary=data['salary'],
            location=data['location'],
            requirements=data['requirements'],
            contact=data['contact'],
            details=data['details'],
            date=date.today()
        )
        
        db.session.add(new_job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': new_job.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': '请先登录管理员账号'}), 401
    
    job = TutoringJobs.query.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': '订单不存在'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '缺少请求数据'}), 400
    
    update_fields = ['title', 'district', 'category', 'grade', 'subject', 'salary', 'location', 'requirements', 'contact', 'details']
    for field in update_fields:
        if field in data:
            setattr(job, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': '请先登录管理员账号'}), 401
    
    job = TutoringJobs.query.get(job_id)
    if not job:
        return jsonify({'success': False, 'error': '订单不存在'}), 404
    
    try:
        db.session.delete(job)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# 静态文件路由
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# 初始化数据库
def initialize_database():
    with app.app_context():
        db.create_all()
        print("数据库表创建成功或已存在")
        
        # 添加初始管理员账户
        if not AdminUsers.query.first():
            admin1 = AdminUsers(username='17689209183', password='940916')
            admin2 = AdminUsers(username='admin', password='admin123')
            db.session.add(admin1)
            db.session.add(admin2)
            db.session.commit()
            print("创建初始管理员: 17689209183/940916 和 admin/admin123")

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True, port=5000)