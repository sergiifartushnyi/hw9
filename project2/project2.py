from celery import Celery
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from tasks import send_contract_email
from hw9.project2.forms import RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='Available')

class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    status = db.Column(db.String(50), default='Pending')

    user = db.relationship('User', backref=db.backref('contracts', lazy=True))
    item = db.relationship('Item', backref=db.backref('contracts', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

@app.route('/')
def index():
    items = Item.query.all()
    return render_template('index.html', items=items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    user_items = Item.query.filter_by(owner_id=current_user.id).all()
    return render_template('profile.html', user=current_user, items=user_items)

@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    name = request.form['name'].strip()
    if not name:
        flash('Item name cannot be empty!', 'danger')
        return redirect(url_for('profile'))
    new_item = Item(name=name, owner_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    flash('Item added successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('profile'))
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', 'info')
    return redirect(url_for('profile'))

@app.route('/create_contract/<int:item_id>', methods=['POST'])
@login_required
def create_contract(item_id):
    item = Item.query.get(item_id)
    if item:
        send_contract_email.delay(current_user.username, f'Contract for {item.name}', 'Your contract body text here')
        flash('Contract created and email sent!', 'success')
    else:
        flash('Item not found!', 'danger')
    return redirect(url_for('contracts'))

@app.route('/contracts')
@login_required
def contracts():
    user_contracts = Contract.query.filter_by(user_id=current_user.id).all()
    return render_template('contracts.html', contracts=user_contracts)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
