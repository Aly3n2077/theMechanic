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
        
        user = data.get_user_by_id(session['user_id'])
        if not user or not user.is_mechanic:
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
        
        user = data.get_user_by_id(session['user_id'])
        if not user or user.is_mechanic:
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
        
        # Prevent booking in the past
        if date < datetime.now().date():
            return []
            
        day_name = date.strftime("%A")
        
        # Check if mechanic works on this day by looking for available TimeSlot objects for this day
        day_slots = [slot for slot in mechanic.availability if slot.day == day_name and slot.available]
        if not day_slots:
            return []
        
        # Process mechanic's working hours for this day
        time_slots = []
        service = data.get_service_by_id(service_id)
        if not service:
            return []
            
        duration_mins = service.duration_minutes
        
        # Generate available time slots from the mechanic's schedule
        for slot in day_slots:
            # Use the correct attribute names from the TimeSlot model
            start_time = datetime.strptime(slot.start_time, "%H:%M").time()
            end_time = datetime.strptime(slot.end_time, "%H:%M").time()
            
            # Generate time slots
            current_time = datetime.combine(date, start_time)
            end_datetime = datetime.combine(date, end_time)
            
            # Create 30-minute interval slots
            while current_time + timedelta(minutes=duration_mins) <= end_datetime:
                # Check if this time slot conflicts with existing bookings
                conflicts = False
                
                for booking in data.get_bookings_by_mechanic(mechanic.id):
                    # Only check confirmed or pending bookings
                    if booking.status not in ["Confirmed", "Pending"]:
                        continue
                        
                    # Check if booking is on the same day
                    if booking.booking_date != date_str:
                        continue
                        
                    # Convert booking time to datetime for comparison
                    booking_time = datetime.strptime(booking.booking_time, "%H:%M").time()
                    booking_datetime = datetime.combine(date, booking_time)
                    
                    # Get the service duration for this booking
                    booking_service = data.get_service_by_id(booking.service_id)
                    booking_duration = booking_service.duration_minutes if booking_service else 60
                    
                    # Check for time slot conflict
                    booking_end = booking_datetime + timedelta(minutes=booking_duration)
                    potential_slot_end = current_time + timedelta(minutes=duration_mins)
                    
                    # If potential slot overlaps with existing booking
                    if (current_time <= booking_datetime < potential_slot_end or
                        current_time < booking_end <= potential_slot_end or
                        (booking_datetime <= current_time and booking_end >= potential_slot_end)):
                        conflicts = True
                        break
                
                # Only add non-conflicting time slots
                if not conflicts:
                    # Don't allow booking times in the past on today's date
                    if date == datetime.now().date() and current_time.time() <= datetime.now().time():
                        pass
                    else:
                        time_slots.append(current_time.strftime("%H:%M"))
                
                current_time += timedelta(minutes=30)  # 30-minute intervals
        
        return sorted(time_slots) # Return sorted time slots for better UX
    except Exception as e:
        print(f"Error getting available times: {e}")
        return []

def get_booking_details(booking_id, user_id):
    """Get detailed information about a booking"""
    # Get booking by checking both customer and mechanic bookings
    user = data.get_user_by_id(user_id)
    if not user:
        return None
    
    if user.is_mechanic and user.mechanic_id:
        bookings = data.get_bookings_by_mechanic(user.mechanic_id)
    else:
        bookings = data.get_bookings_by_customer(user_id)
    
    booking = next((b for b in bookings if b.id == booking_id), None)
    if not booking:
        return None
    
    customer = data.get_user_by_id(booking.customer_id)
    mechanic = data.get_mechanic_by_id(booking.mechanic_id)
    service = data.get_service_by_id(booking.service_id)
    vehicle = data.get_vehicle_by_id(booking.vehicle_id)
    
    return {
        'booking': booking,
        'customer': customer,
        'mechanic': mechanic,
        'service': service,
        'vehicle': vehicle
    }
