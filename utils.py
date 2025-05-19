from functools import wraps
from flask import session, flash, redirect, url_for, request
import data
from datetime import datetime, timedelta

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def mechanic_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user = data.get_user(session['user_id'])
        if not user or user.user_type != 'mechanic':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        
        user = data.get_user(session['user_id'])
        if not user or user.user_type != 'customer':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

def parse_datetime(date_str, time_str):
    """Convert date and time strings to a datetime object"""
    try:
        datetime_str = f"{date_str} {time_str}"
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        return None

def format_datetime(dt):
    """Format datetime object to string"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M")

def get_available_times(mechanic, date_str, service_id):
    """Get available appointment times for a mechanic on a given date"""
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_name = date.strftime("%A").lower()
        
        # Check if mechanic works on this day
        if day_name not in mechanic.availability or not mechanic.availability[day_name]:
            return []
        
        # Get working hours
        hours = mechanic.availability[day_name]
        start_time = datetime.strptime(hours["start"], "%H:%M").time()
        end_time = datetime.strptime(hours["end"], "%H:%M").time()
        
        # Get service duration
        service = data.get_service(service_id)
        if not service:
            return []
        duration = service.duration  # in minutes
        
        # Generate time slots
        current_time = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        time_slots = []
        
        while current_time + timedelta(minutes=duration) <= end_datetime:
            # Check if this time slot conflicts with existing appointments
            conflicts = False
            
            for appt in data.get_mechanic_appointments(mechanic.id):
                if isinstance(appt.date_time, str):
                    appt_datetime = datetime.fromisoformat(appt.date_time)
                else:
                    appt_datetime = appt.date_time
                
                appt_service = data.get_service(appt.service_id)
                appt_duration = appt_service.duration if appt_service else 60
                
                # Check if appointment is on the same day and status is not 'cancelled'
                if (appt_datetime.date() == date and appt.status != 'cancelled' and
                    (current_time <= appt_datetime < current_time + timedelta(minutes=duration) or
                     current_time < appt_datetime + timedelta(minutes=appt_duration) <= current_time + timedelta(minutes=duration))):
                    conflicts = True
                    break
            
            if not conflicts:
                time_slots.append(current_time.strftime("%H:%M"))
            
            current_time += timedelta(minutes=30)  # 30-minute intervals
        
        return time_slots
    except Exception as e:
        print(f"Error getting available times: {e}")
        return []

def get_appointment_details(appointment_id):
    """Get detailed information about an appointment"""
    appointment = data.get_appointment(appointment_id)
    if not appointment:
        return None
    
    customer = data.get_user(appointment.customer_id)
    mechanic = data.get_mechanic(appointment.mechanic_id)
    service = data.get_service(appointment.service_id)
    
    return {
        'appointment': appointment,
        'customer': customer,
        'mechanic': mechanic,
        'service': service
    }
