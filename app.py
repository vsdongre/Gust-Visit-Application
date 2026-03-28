from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///visits.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(100), nullable=False)
    guest_email = db.Column(db.String(120), nullable=False)
    guest_phone = db.Column(db.String(20), nullable=True)
    host_name = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(255), nullable=False)
    check_in = db.Column(db.DateTime, nullable=False, default=utcnow)
    check_out = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    @property
    def is_checked_in(self):
        return self.check_out is None

    @property
    def duration(self):
        if self.check_out:
            delta = self.check_out - self.check_in
            total_minutes = int(delta.total_seconds() // 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return None

    def to_dict(self):
        return {
            'id': self.id,
            'guest_name': self.guest_name,
            'guest_email': self.guest_email,
            'guest_phone': self.guest_phone,
            'host_name': self.host_name,
            'purpose': self.purpose,
            'check_in': self.check_in.strftime('%Y-%m-%d %H:%M'),
            'check_out': self.check_out.strftime('%Y-%m-%d %H:%M') if self.check_out else None,
            'is_checked_in': self.is_checked_in,
            'duration': self.duration,
            'notes': self.notes,
        }


@app.route('/')
def index():
    active_visits = Visit.query.filter_by(check_out=None).order_by(Visit.check_in.desc()).all()
    return render_template('index.html', active_visits=active_visits)


@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        guest_name = request.form.get('guest_name', '').strip()
        guest_email = request.form.get('guest_email', '').strip()
        guest_phone = request.form.get('guest_phone', '').strip()
        host_name = request.form.get('host_name', '').strip()
        purpose = request.form.get('purpose', '').strip()
        notes = request.form.get('notes', '').strip()

        errors = []
        if not guest_name:
            errors.append('Guest name is required.')
        if not guest_email:
            errors.append('Guest email is required.')
        if not host_name:
            errors.append('Host name is required.')
        if not purpose:
            errors.append('Purpose of visit is required.')

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('checkin.html', form_data=request.form)

        visit = Visit(
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone if guest_phone else None,
            host_name=host_name,
            purpose=purpose,
            notes=notes if notes else None,
        )
        db.session.add(visit)
        db.session.commit()
        flash(f'Welcome, {guest_name}! You have been checked in successfully.', 'success')
        return redirect(url_for('index'))

    return render_template('checkin.html', form_data={})


@app.route('/checkout/<int:visit_id>', methods=['POST'])
def checkout(visit_id):
    visit = db.session.get(Visit, visit_id)
    if not visit:
        flash('Visit not found.', 'danger')
        return redirect(url_for('index'))
    if visit.check_out is not None:
        flash('Guest has already checked out.', 'warning')
        return redirect(url_for('index'))
    visit.check_out = utcnow()
    db.session.commit()
    flash(f'{visit.guest_name} has been checked out. Visit duration: {visit.duration}.', 'success')
    return redirect(url_for('index'))


@app.route('/log')
def visit_log():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    search = request.args.get('search', '').strip()
    status = request.args.get('status', 'all')

    query = Visit.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                Visit.guest_name.ilike(like),
                Visit.guest_email.ilike(like),
                Visit.host_name.ilike(like),
                Visit.purpose.ilike(like),
            )
        )

    if status == 'active':
        query = query.filter(Visit.check_out.is_(None))
    elif status == 'completed':
        query = query.filter(Visit.check_out.isnot(None))

    pagination = query.order_by(Visit.check_in.desc()).paginate(page=page, per_page=per_page, error_out=False)
    visits = pagination.items

    return render_template('log.html', visits=visits, pagination=pagination, search=search, status=status)


@app.route('/visit/<int:visit_id>')
def visit_detail(visit_id):
    visit = db.session.get(Visit, visit_id)
    if not visit:
        flash('Visit not found.', 'danger')
        return redirect(url_for('visit_log'))
    return render_template('visit_detail.html', visit=visit)


@app.route('/api/active-visits')
def api_active_visits():
    visits = Visit.query.filter_by(check_out=None).order_by(Visit.check_in.desc()).all()
    return jsonify([v.to_dict() for v in visits])


@app.route('/api/stats')
def api_stats():
    total = Visit.query.count()
    active = Visit.query.filter_by(check_out=None).count()
    today = utcnow().date()
    today_visits = Visit.query.filter(
        db.func.date(Visit.check_in) == today
    ).count()
    return jsonify({
        'total_visits': total,
        'active_visitors': active,
        'today_visits': today_visits,
    })


@app.context_processor
def inject_now():
    return {'now': utcnow()}


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
