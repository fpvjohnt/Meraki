from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from .models import User, Organization

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class ThresholdForm(FlaskForm):
    organization = SelectField('Organization', coerce=int, validators=[DataRequired()])
    channel_utilization = FloatField('5G Channel Utilization (%)', validators=[DataRequired()])
    occurrences_warning = FloatField('5G Occurrences Warning', validators=[DataRequired()])
    occurrences_alarm = FloatField('5G Occurrences Alarm', validators=[DataRequired()])
    min_tx_power = FloatField('5G Min TX Power (dBm)', validators=[DataRequired()])
    min_bitrate = FloatField('5G Min Bitrate (Mbps)', validators=[DataRequired()])
    max_channel_width = FloatField('5G Max Channel Width (MHz)', validators=[DataRequired()])
    broadcast_rate = FloatField('Broadcast Rate (pps)', validators=[DataRequired()])
    multicast_rate = FloatField('Multicast Rate (pps)', validators=[DataRequired()])
    topology_changes = FloatField('Topology Changes', validators=[DataRequired()])
    ssid_amount = FloatField('SSID Amount', validators=[DataRequired()])
    submit = SubmitField('Update Thresholds')

class OrganizationForm(FlaskForm):
    name = StringField('Organization Name', validators=[DataRequired()])
    meraki_org_id = StringField('Meraki Organization ID', validators=[DataRequired()])
    api_key = StringField('API Key', validators=[DataRequired()])
    submit = SubmitField('Add Organization')

class RecurringHealthCheckForm(FlaskForm):
    organization = SelectField('Organization', coerce=int, validators=[DataRequired()])
    frequency = SelectField('Frequency', choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], validators=[DataRequired()])
    config_path = StringField('Config Path', validators=[DataRequired()])
    submit = SubmitField('Schedule Recurring Health Check')