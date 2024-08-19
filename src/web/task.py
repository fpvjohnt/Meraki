from .celery_app import make_celery
from . import create_app, db
from .models import User, HealthCheckResult, RecurringHealthCheck, Organization
import meraki_health_check
from flask_mail import Message
from . import mail
from datetime import datetime, timedelta

app = create_app()
celery = make_celery(app)

@celery.task
def run_scheduled_health_check(user_id, org_id, config_path):
    with app.app_context():
        user = User.query.get(user_id)
        organization = Organization.query.get(org_id)
        if user and organization:
            results = meraki_health_check.run_health_check(config_path, user_id, org_id)
            new_result = HealthCheckResult(user_id=user.id, organization_id=org_id, results=results)
            db.session.add(new_result)
            db.session.commit()
            
            # Send email notification
            send_health_check_email(user, organization, results)

def send_health_check_email(user, organization, results):
    msg = Message('Meraki Health Check Results',
                  sender='noreply@merakihealthcheck.com',
                  recipients=[user.email])
    msg.body = render_template('email/health_check_results.txt', user=user, organization=organization, results=results)
    msg.html = render_template('email/health_check_results.html', user=user, organization=organization, results=results)
    mail.send(msg)

@celery.task
def run_recurring_health_checks():
    with app.app_context():
        now = datetime.utcnow()
        due_checks = RecurringHealthCheck.query.filter(RecurringHealthCheck.next_run <= now).all()
        
        for check in due_checks:
            run_scheduled_health_check.delay(check.user_id, check.organization_id, check.config_path)
            
            if check.frequency == 'daily':
                check.next_run = now + timedelta(days=1)
            elif check.frequency == 'weekly':
                check.next_run = now + timedelta(weeks=1)
            elif check.frequency == 'monthly':
                check.next_run = now + timedelta(days=30)
            
            db.session.commit()

# Schedule the recurring health checks task to run every hour
@celery.task
def schedule_recurring_health_checks():
    run_recurring_health_checks.delay()

# Run the scheduler every hour
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3600.0, schedule_recurring_health_checks.s(), name='Schedule recurring health checks every hour')