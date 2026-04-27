from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wattsaver-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wattsaver.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── MODELS ────────────────────────────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    cost_per_unit = db.Column(db.Float, default=25.0)  # KES per kWh
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    appliances = db.relationship('Appliance', backref='user', lazy=True, cascade='all, delete-orphan')

class Appliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    power_watts = db.Column(db.Float, nullable=False)
    hours_per_day = db.Column(db.Float, nullable=False)
    days_per_week = db.Column(db.Float, nullable=False, default=7)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def daily_kwh(self):
        return (self.power_watts * self.hours_per_day) / 1000

    @property
    def weekly_kwh(self):
        return self.daily_kwh * self.days_per_week

    @property
    def monthly_kwh(self):
        return self.daily_kwh * (self.days_per_week / 7) * 30

    def monthly_cost(self, rate):
        return self.monthly_kwh * rate

    def to_dict(self, rate=25.0):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'power_watts': self.power_watts,
            'hours_per_day': self.hours_per_day,
            'days_per_week': self.days_per_week,
            'daily_kwh': round(self.daily_kwh, 3),
            'weekly_kwh': round(self.weekly_kwh, 3),
            'monthly_kwh': round(self.monthly_kwh, 3),
            'daily_cost': round(self.daily_kwh * rate, 2),
            'monthly_cost': round(self.monthly_cost(rate), 2),
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def get_recommendations(appliances, rate):
    recs = []
    for a in appliances:
        if a.category == 'Heating/Cooling' and a.hours_per_day > 8:
            savings = round((a.hours_per_day - 6) * a.power_watts / 1000 * 30 * rate, 0)
            recs.append({'appliance': a.name, 'icon': '❄️',
                'tip': f"Running {a.name} for {a.hours_per_day}h/day is costly. Limit to 6h/day — saves ~KES {savings}/month.",
                'savings': savings, 'severity': 'high'})
        if a.category == 'Lighting' and a.power_watts > 40:
            savings = round((a.power_watts - 9) / 1000 * a.hours_per_day * (a.days_per_week / 7) * 30 * rate, 0)
            recs.append({'appliance': a.name, 'icon': '💡',
                'tip': f"Replace {a.name} ({a.power_watts}W) with a 9W LED — saves ~KES {savings}/month.",
                'savings': savings, 'severity': 'medium'})
        if a.category == 'Entertainment' and a.hours_per_day > 6:
            savings = round((a.hours_per_day - 4) * a.power_watts / 1000 * (a.days_per_week / 7) * 30 * rate, 0)
            recs.append({'appliance': a.name, 'icon': '📺',
                'tip': f"{a.name} runs {a.hours_per_day}h/day. Reducing to 4h saves ~KES {savings}/month.",
                'savings': savings, 'severity': 'low'})
        if a.power_watts > 1500 and a.hours_per_day > 2:
            savings = round(a.monthly_kwh * rate * 0.1, 0)
            recs.append({'appliance': a.name, 'icon': '⚡',
                'tip': f"{a.name} is high-power ({a.power_watts}W). Use during off-peak hours (10pm–6am) to save ~KES {savings}/month.",
                'savings': savings, 'severity': 'medium'})
    recs.sort(key=lambda x: x['savings'], reverse=True)
    return recs[:6]

def get_peak_analysis(appliances):
    hvac_power = sum(a.power_watts for a in appliances if a.category == 'Heating/Cooling')
    kitchen_power = sum(a.power_watts for a in appliances if a.category == 'Kitchen')
    office_power = sum(a.power_watts for a in appliances if a.category == 'Office/Work')
    entertainment_power = sum(a.power_watts for a in appliances if a.category == 'Entertainment')
    lighting_power = sum(a.power_watts for a in appliances if a.category == 'Lighting')
    return {
        'Morning (6am-9am)': round((hvac_power * 0.5 + kitchen_power * 0.8) / 1000, 2),
        'Daytime (9am-5pm)': round((office_power + hvac_power * 0.3) / 1000, 2),
        'Evening (5pm-11pm)': round((entertainment_power + lighting_power + kitchen_power * 0.5 + hvac_power * 0.7) / 1000, 2),
        'Night (11pm-6am)': round((hvac_power * 0.2) / 1000, 2)
    }

# ─── AUTH ROUTES ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    user = User(username=data['username'], email=data['email'],
                password_hash=generate_password_hash(data['password']))
    db.session.add(user)
    db.session.commit()
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({'success': True})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

# ─── API ROUTES ────────────────────────────────────────────────────────────────

@app.route('/api/appliances', methods=['GET'])
def get_appliances():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    appliances = Appliance.query.filter_by(user_id=user.id).order_by(Appliance.monthly_kwh.desc()).all()
    return jsonify([a.to_dict(user.cost_per_unit) for a in appliances])

@app.route('/api/appliances', methods=['POST'])
def add_appliance():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    appliance = Appliance(
        user_id=session['user_id'],
        name=data['name'], category=data['category'],
        power_watts=float(data['power_watts']),
        hours_per_day=float(data['hours_per_day']),
        days_per_week=float(data.get('days_per_week', 7))
    )
    db.session.add(appliance)
    db.session.commit()
    user = User.query.get(session['user_id'])
    return jsonify(appliance.to_dict(user.cost_per_unit)), 201

@app.route('/api/appliances/<int:aid>', methods=['PUT'])
def update_appliance(aid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    appliance = Appliance.query.filter_by(id=aid, user_id=session['user_id']).first_or_404()
    data = request.get_json()
    for field in ['name', 'category', 'power_watts', 'hours_per_day', 'days_per_week']:
        if field in data:
            setattr(appliance, field, float(data[field]) if field != 'name' and field != 'category' else data[field])
    db.session.commit()
    user = User.query.get(session['user_id'])
    return jsonify(appliance.to_dict(user.cost_per_unit))

@app.route('/api/appliances/<int:aid>', methods=['DELETE'])
def delete_appliance(aid):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    appliance = Appliance.query.filter_by(id=aid, user_id=session['user_id']).first_or_404()
    db.session.delete(appliance)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/summary')
def get_summary():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    appliances = Appliance.query.filter_by(user_id=user.id).all()
    if not appliances:
        return jsonify({'total_appliances': 0, 'daily_kwh': 0, 'monthly_kwh': 0,
                        'monthly_cost': 0, 'daily_cost': 0, 'category_breakdown': {},
                        'top_consumers': [], 'peak_analysis': {}, 'recommendations': []})
    total_daily_kwh = sum(a.daily_kwh for a in appliances)
    total_monthly_kwh = sum(a.monthly_kwh for a in appliances)
    categories = {}
    for a in appliances:
        cat = a.category
        if cat not in categories:
            categories[cat] = {'kwh': 0, 'cost': 0, 'count': 0}
        categories[cat]['kwh'] = round(categories[cat]['kwh'] + a.monthly_kwh, 3)
        categories[cat]['cost'] = round(categories[cat]['cost'] + a.monthly_cost(user.cost_per_unit), 2)
        categories[cat]['count'] += 1
    top = sorted(appliances, key=lambda x: x.monthly_kwh, reverse=True)[:5]
    return jsonify({
        'total_appliances': len(appliances),
        'daily_kwh': round(total_daily_kwh, 3),
        'monthly_kwh': round(total_monthly_kwh, 3),
        'daily_cost': round(total_daily_kwh * user.cost_per_unit, 2),
        'monthly_cost': round(total_monthly_kwh * user.cost_per_unit, 2),
        'category_breakdown': categories,
        'top_consumers': [{'name': a.name, 'monthly_kwh': round(a.monthly_kwh, 2),
                           'monthly_cost': round(a.monthly_cost(user.cost_per_unit), 2)} for a in top],
        'peak_analysis': get_peak_analysis(appliances),
        'recommendations': get_recommendations(appliances, user.cost_per_unit)
    })

@app.route('/api/settings', methods=['GET', 'PUT'])
def settings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(session['user_id'])
    if request.method == 'PUT':
        data = request.get_json()
        if 'cost_per_unit' in data:
            user.cost_per_unit = float(data['cost_per_unit'])
        db.session.commit()
        return jsonify({'success': True, 'cost_per_unit': user.cost_per_unit})
    return jsonify({'cost_per_unit': user.cost_per_unit, 'username': user.username, 'email': user.email})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
