import os
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from forms import LoginForm, RegistrationForm, VehicleForm, BookingForm
import data

def register_routes(app):
    
    @app.route('/')
    def index():
        """Homepage with featured mechanics and services"""
        featured_mechanics = data.get_mechanics()[:3]  # Get first 3 for featured section
        services = data.get_services()
        return render_template('index.html', 
                              featured_mechanics=featured_mechanics,
                              services=services)
    
    @app.route('/mechanics')
    def mechanics_list():
        """List all mechanics"""
        mechanics = data.get_mechanics()
        services = data.get_services()
        return render_template('mechanics.html', mechanics=mechanics, services=services)
    
    @app.route('/mechanics/<int:mechanic_id>')
    def mechanic_detail(mechanic_id):
        """Show detailed page for a specific mechanic"""
        mechanic = data.get_mechanic_by_id(mechanic_id)
        if not mechanic:
            flash('Mechanic not found.', 'danger')
            return redirect(url_for('mechanics_list'))
        
        services = data.get_mechanic_services(mechanic_id)
        return render_template('mechanic_detail.html', 
                              mechanic=mechanic, 
                              services=services)
    
    @app.route('/book/<int:mechanic_id>', methods=['GET', 'POST'])
    def book_mechanic(mechanic_id):
        """Booking form for a specific mechanic"""
        if 'user_id' not in session:
            flash('Please log in to book a mechanic.', 'warning')
            return redirect(url_for('login', next=request.path))
        
        mechanic = data.get_mechanic_by_id(mechanic_id)
        if not mechanic:
            flash('Mechanic not found.', 'danger')
            return redirect(url_for('mechanics_list'))
        
        form = BookingForm()
        
        # Get the mechanic's services for the dropdown
        mechanic_services = data.get_mechanic_services(mechanic_id)
        form.service_id.choices = [(s.id, f"{s.name} - ${s.price:.2f}") for s in mechanic_services]
        
        # Get user's vehicles for the dropdown
        user_vehicles = data.get_vehicles_by_user(session['user_id'])
        if not user_vehicles:
            flash('You need to add a vehicle first.', 'warning')
            return redirect(url_for('add_vehicle', next=request.path))
        
        form.vehicle_id.choices = [(v.id, f"{v.make} {v.model} ({v.year})") for v in user_vehicles]
        
        # Generate time slots based on mechanic availability
        time_slots = []
        for availability in mechanic.availability:
            if availability.available:
                # Convert to datetime objects for manipulation
                start_time = datetime.strptime(availability.start_time, '%H:%M')
                end_time = datetime.strptime(availability.end_time, '%H:%M')
                
                current_time = start_time
                while current_time < end_time:
                    time_slots.append(current_time.strftime('%H:%M'))
                    current_time += timedelta(minutes=60)  # 1-hour slots
        
        form.booking_time.choices = [(slot, slot) for slot in time_slots]
        
        if form.validate_on_submit():
            booking = data.create_booking(
                customer_id=session['user_id'],
                mechanic_id=mechanic_id,
                service_id=form.service_id.data,
                vehicle_id=form.vehicle_id.data,
                booking_date=form.booking_date.data.strftime('%Y-%m-%d') if form.booking_date.data else None,
                booking_time=form.booking_time.data,
                issue_description=form.issue_description.data
            )
            
            flash('Booking submitted successfully!', 'success')
            return redirect(url_for('booking_confirmation', booking_id=booking.id))
        
        return render_template('booking.html', 
                              form=form, 
                              mechanic=mechanic)
    
    @app.route('/booking/confirmation/<int:booking_id>')
    def booking_confirmation(booking_id):
        """Confirmation page after successful booking"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        booking = next((b for b in data.get_bookings_by_customer(session['user_id']) 
                      if b.id == booking_id), None)
        
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('customer_dashboard'))
        
        service = data.get_service_by_id(booking.service_id)
        mechanic = data.get_mechanic_by_id(booking.mechanic_id)
        
        return render_template('confirmation.html', 
                              booking=booking,
                              service=service,
                              mechanic=mechanic)
    
    @app.route('/dashboard')
    def dashboard():
        """Redirect to the appropriate dashboard based on user type"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = data.get_user_by_id(session['user_id'])
        if user and user.is_mechanic:
            return redirect(url_for('mechanic_dashboard'))
        else:
            return redirect(url_for('customer_dashboard'))
    
    @app.route('/dashboard/customer')
    def customer_dashboard():
        """Dashboard for customers to see bookings and vehicles"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = data.get_user_by_id(session['user_id'])
        if user and user.is_mechanic:
            return redirect(url_for('mechanic_dashboard'))
        
        bookings = data.get_bookings_by_customer(session['user_id'])
        vehicles = data.get_vehicles_by_user(session['user_id'])
        
        # Split bookings by status
        upcoming = [b for b in bookings if b.status in ["Pending", "Confirmed"] 
                   and datetime.strptime(b.booking_date, '%Y-%m-%d') >= datetime.now()]
        past = [b for b in bookings if b.status in ["Completed", "Cancelled"] 
               or datetime.strptime(b.booking_date, '%Y-%m-%d') < datetime.now()]
        
        return render_template('customer_dashboard.html',
                              user=user,
                              upcoming_bookings=upcoming,
                              past_bookings=past,
                              vehicles=vehicles)
    
    @app.route('/dashboard/mechanic')
    def mechanic_dashboard():
        """Dashboard for mechanics to manage bookings"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = data.get_user_by_id(session['user_id'])
        if not user.is_mechanic:
            return redirect(url_for('customer_dashboard'))
        
        mechanic = data.get_mechanic_by_id(user.mechanic_id)
        if not mechanic:
            flash('Mechanic profile not found.', 'danger')
            return redirect(url_for('index'))
        
        bookings = data.get_bookings_by_mechanic(mechanic.id)
        
        # Split bookings by status and date
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming = [b for b in bookings if b.status in ["Pending", "Confirmed"] 
                   and b.booking_date >= today]
        completed = [b for b in bookings if b.status == "Completed"]
        
        return render_template('mechanic_dashboard.html',
                              user=user,
                              mechanic=mechanic,
                              upcoming_bookings=upcoming,
                              completed_bookings=completed)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = data.get_user_by_email(form.email.data)
            
            if user and check_password_hash(user.password_hash, form.password.data):
                session['user_id'] = user.id
                next_page = request.args.get('next')
                
                flash(f'Welcome back, {user.name}!', 'success')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Login failed. Please check your email and password.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        
        if form.validate_on_submit():
            existing_user = data.get_user_by_email(form.email.data)
            
            if existing_user:
                flash('Email already registered. Please log in.', 'warning')
                return redirect(url_for('login'))
            
            user = data.register_user(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data
            )
            
            if user:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'danger')
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    def logout():
        """Log out the current user"""
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/vehicles/add', methods=['GET', 'POST'])
    def add_vehicle():
        """Add a vehicle for the current user"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        form = VehicleForm()
        
        if form.validate_on_submit():
            vehicle = data.add_vehicle(
                user_id=session['user_id'],
                make=form.make.data,
                model=form.model.data,
                year=form.year.data,
                license_plate=form.license_plate.data
            )
            
            flash('Vehicle added successfully!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('customer_dashboard'))
        
        return render_template('add_vehicle.html', form=form)
    
    @app.route('/api/update_booking_status', methods=['POST'])
    def update_booking_status():
        """API endpoint to update a booking status"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
        booking_id = request.json.get('booking_id')
        new_status = request.json.get('status')
        
        if not booking_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing data'}), 400
        
        updated_booking = data.update_booking_status(int(booking_id), new_status)
        
        if updated_booking:
            return jsonify({'success': True, 'message': f'Booking status updated to {new_status}'})
        else:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
