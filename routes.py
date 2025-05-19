import os
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
from forms import LoginForm, RegistrationForm, VehicleForm, BookingForm, ReviewForm, VehicleListingForm, VehicleSearchForm, ProfileForm
import data
import utils

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
        """List all mechanics with optional filtering"""
        mechanics = data.get_mechanics()
        services = data.get_services()
        
        # Filter by service if provided
        service_id = request.args.get('service_id')
        if service_id and service_id.isdigit():
            service_id = int(service_id)
            mechanics = [m for m in mechanics if service_id in m.services]
            
        # Filter by specialization if provided
        specialization = request.args.get('specialization')
        if specialization:
            mechanics = [m for m in mechanics if specialization.lower() in m.specialization.lower()]
            
        # Search by issue description
        issue_description = request.args.get('issue')
        if issue_description:
            # Get recommended services for this issue
            recommended_service_ids = data.recommend_services(issue_description)
            if recommended_service_ids:
                # Filter mechanics who offer these services
                filtered_mechanics = []
                for mechanic in mechanics:
                    for service_id in recommended_service_ids:
                        if service_id in mechanic.services:
                            filtered_mechanics.append(mechanic)
                            break
                mechanics = filtered_mechanics
        
        return render_template('mechanics.html', 
                             mechanics=mechanics, 
                             services=services,
                             selected_service=service_id if 'service_id' in request.args else None,
                             issue_description=issue_description)
    
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
        
        # If issue description is provided in GET parameter, analyze it to recommend services
        issue_description = request.args.get('issue')
        recommended_service_id = None
        
        if issue_description and request.method == 'GET':
            recommended_service_ids = data.recommend_services(issue_description)
            if recommended_service_ids:
                # Find the first recommended service that this mechanic offers
                for service_id in recommended_service_ids:
                    if service_id in mechanic.services:
                        recommended_service_id = service_id
                        break
            
            # Pre-populate the issue description field
            form.issue_description.data = issue_description
        
        # If we have a date parameter, use it to generate available time slots
        selected_date = request.args.get('date')
        if not selected_date and form.booking_date.data:
            selected_date = form.booking_date.data.strftime('%Y-%m-%d')
        
        # Get available time slots for this date and service
        time_slots = []
        if selected_date and form.service_id.data:
            time_slots = utils.get_available_times(mechanic, selected_date, form.service_id.data)
        elif selected_date and recommended_service_id:
            time_slots = utils.get_available_times(mechanic, selected_date, recommended_service_id)
        else:
            # Generate some default time slots if we can't determine availability yet
            for availability in mechanic.availability:
                if availability.available:
                    # Convert to datetime objects for manipulation
                    start_time = datetime.strptime(availability.start_time, '%H:%M')
                    end_time = datetime.strptime(availability.end_time, '%H:%M')
                    
                    current_time = start_time
                    while current_time < end_time:
                        time_slots.append(current_time.strftime('%H:%M'))
                        current_time += timedelta(minutes=60)  # 1-hour slots
        
        # Set the available time slots
        form.booking_time.choices = [(slot, slot) for slot in time_slots]
        
        # If we have a recommended service, select it by default
        if recommended_service_id and request.method == 'GET':
            form.service_id.data = recommended_service_id
        
        if form.validate_on_submit():
            # Get the selected service to validate duration fits in the mechanic's schedule
            selected_service = data.get_service_by_id(form.service_id.data)
            if not selected_service:
                flash('Selected service is not available. Please choose another service.', 'danger')
                return redirect(url_for('book_mechanic', mechanic_id=mechanic_id))
                
            booking_date = form.booking_date.data.strftime('%Y-%m-%d') if form.booking_date.data else None
            
            # Validate the time slot is still available (to handle race conditions)
            available_times = utils.get_available_times(mechanic, booking_date, selected_service.id)
            if form.booking_time.data not in available_times:
                flash('Sorry, this time slot is no longer available. Please select another time.', 'danger')
                return redirect(url_for('book_mechanic', mechanic_id=mechanic_id))
            
            # Create the booking
            booking = data.create_booking(
                customer_id=session['user_id'],
                mechanic_id=mechanic_id,
                service_id=form.service_id.data,
                vehicle_id=form.vehicle_id.data,
                booking_date=booking_date,
                booking_time=form.booking_time.data,
                issue_description=form.issue_description.data
            )
            
            flash('Booking submitted successfully!', 'success')
            return redirect(url_for('booking_confirmation', booking_id=booking.id))
        
        return render_template('booking.html', 
                              form=form, 
                              mechanic=mechanic,
                              recommended_service_id=recommended_service_id)
    
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
        
        # Get any unread notifications for this user
        notifications = data.get_notifications_by_user(session['user_id'])
        
        # Split bookings by status
        upcoming = [b for b in bookings if b.status in ["Pending", "Confirmed"] 
                   and datetime.strptime(b.booking_date, '%Y-%m-%d') >= datetime.now()]
        past = [b for b in bookings if b.status in ["Completed", "Cancelled"] 
               or datetime.strptime(b.booking_date, '%Y-%m-%d') < datetime.now()]
        
        # Find any completed bookings that need reviews
        need_review = [b for b in past if b.status == "Completed" and not b.has_review]
        
        return render_template('customer_dashboard.html',
                              user=user,
                              upcoming_bookings=upcoming,
                              past_bookings=past,
                              need_review=need_review,
                              vehicles=vehicles,
                              notifications=notifications)
    
    @app.route('/dashboard/mechanic')
    def mechanic_dashboard():
        """Dashboard for mechanics to manage bookings"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user = data.get_user_by_id(session['user_id'])
        if not user or not user.is_mechanic:
            return redirect(url_for('customer_dashboard'))
        
        mechanic = data.get_mechanic_by_id(user.mechanic_id) if user.mechanic_id else None
        if not mechanic:
            flash('Mechanic profile not found.', 'danger')
            return redirect(url_for('index'))
        
        bookings = data.get_bookings_by_mechanic(mechanic.id)
        
        # Get any unread notifications for this user
        notifications = data.get_notifications_by_user(session['user_id'])
        
        # Split bookings by status and date
        today = datetime.now().strftime('%Y-%m-%d')
        pending = [b for b in bookings if b.status == "Pending"]
        confirmed = [b for b in bookings if b.status == "Confirmed" and b.booking_date >= today]
        completed = [b for b in bookings if b.status == "Completed"]
        
        # Get reviews for this mechanic
        mechanic_reviews = data.get_reviews_by_mechanic(mechanic.id)
        
        return render_template('mechanic_dashboard.html',
                              user=user,
                              mechanic=mechanic,
                              pending_bookings=pending,
                              confirmed_bookings=confirmed,
                              completed_bookings=completed,
                              reviews=mechanic_reviews,
                              notifications=notifications)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = data.get_user_by_email(form.email.data)
            password_input = form.password.data if form.password.data else ""
            
            if user and check_password_hash(user.password_hash, password_input):
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
            
            # Check if user wants to register as a mechanic
            is_mechanic = form.is_mechanic.data if hasattr(form, 'is_mechanic') else False
            
            user = data.register_user(
                name=form.name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
                is_mechanic=is_mechanic
            )
            
            if user:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Registration failed. Please try again.', 'danger')
        elif request.method == 'POST':
            # If form validation failed, log the errors
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
        
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
        
        # Safely get JSON data
        json_data = request.get_json(silent=True) or {}
        booking_id = json_data.get('booking_id')
        new_status = json_data.get('status')
        
        if not booking_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing data'}), 400
        
        updated_booking = data.update_booking_status(int(booking_id), new_status)
        
        if updated_booking:
            return jsonify({'success': True, 'message': f'Booking status updated to {new_status}'})
        else:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
            
    @app.route('/review/<int:booking_id>', methods=['GET', 'POST'])
    def review_mechanic(booking_id):
        """Leave a review for a mechanic after service completion"""
        if 'user_id' not in session:
            flash('Please log in to leave a review.', 'warning')
            return redirect(url_for('login'))
        
        # Get the booking and verify it belongs to this user and is completed
        customer_bookings = data.get_bookings_by_customer(session['user_id'])
        booking = next((b for b in customer_bookings if b.id == booking_id), None)
        
        if not booking:
            flash('Booking not found.', 'danger')
            return redirect(url_for('customer_dashboard'))
            
        if booking.status != 'Completed':
            flash('You can only review completed bookings.', 'warning')
            return redirect(url_for('customer_dashboard'))
            
        # Check if this booking already has a review
        existing_review = data.get_review_by_booking(booking_id)
        if existing_review:
            flash('You have already reviewed this service.', 'info')
            return redirect(url_for('customer_dashboard'))
        
        form = ReviewForm()
        form.booking_id.data = booking_id
        form.mechanic_id.data = booking.mechanic_id
        
        if form.validate_on_submit():
            review = data.create_review(
                booking_id=booking_id,
                customer_id=session['user_id'],
                mechanic_id=int(form.mechanic_id.data),
                rating=form.rating.data,
                comment=form.comment.data
            )
            
            if review:
                flash('Thank you for your review!', 'success')
                return redirect(url_for('customer_dashboard'))
            else:
                flash('There was an error submitting your review. Please try again.', 'danger')
        
        # Get mechanic and service details for context
        mechanic = data.get_mechanic_by_id(booking.mechanic_id)
        service = data.get_service_by_id(booking.service_id)
        
        return render_template('rate_mechanic.html', 
                              form=form, 
                              booking=booking,
                              mechanic=mechanic,
                              service=service)
                              
    @app.route('/api/suggest_services', methods=['POST'])
    def suggest_services():
        """API endpoint to suggest services based on issue description"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
        
        json_data = request.get_json(silent=True) or {}
        issue_description = json_data.get('issue_description', '')
        
        if not issue_description:
            return jsonify({'success': False, 'message': 'No issue description provided'}), 400
            
        # Get service recommendations
        recommended_service_ids = data.recommend_services(issue_description)
        recommended_services = []
        
        # Only include valid services that exist
        for sid in recommended_service_ids:
            service = data.get_service_by_id(sid)
            if service:
                recommended_services.append(service)
        
        # Format the response data
        services_data = []
        for service in recommended_services:
            services_data.append({
                'id': service.id,
                'name': service.name,
                'price': service.price,
                'description': service.description,
                'duration_minutes': service.duration_minutes,
                'category': service.category
            })
        
        return jsonify({
            'success': True, 
            'recommendations': services_data
        })
        
    @app.route('/api/notifications/mark_read', methods=['POST'])
    def mark_notification_read():
        """API endpoint to mark a notification as read"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
            
        json_data = request.get_json(silent=True) or {}
        notification_id = json_data.get('notification_id')
        
        if not notification_id:
            return jsonify({'success': False, 'message': 'Missing notification ID'}), 400
            
        # Verify this notification belongs to the current user
        notifications = data.get_notifications_by_user(session['user_id'])
        notification = next((n for n in notifications if n.id == int(notification_id)), None)
        
        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found'}), 404
            
        # Mark as read
        result = data.mark_notification_read(int(notification_id))
        
        if result:
            return jsonify({'success': True, 'message': 'Notification marked as read'})
        else:
            return jsonify({'success': False, 'message': 'Failed to mark notification as read'}), 500
            
    @app.route('/api/find_mechanic', methods=['POST'])
    def find_mechanic():
        """API endpoint to find the best mechanic for a specific issue"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
            
        json_data = request.get_json(silent=True) or {}
        issue_description = json_data.get('issue_description', '')
        location = json_data.get('location', '')
        preferred_date = json_data.get('preferred_date', '')
        
        if not issue_description:
            return jsonify({'success': False, 'message': 'No issue description provided'}), 400
        
        # Get recommended services for this issue
        recommended_service_ids = data.recommend_services(issue_description)
        if not recommended_service_ids:
            return jsonify({'success': False, 'message': 'No suitable services found for this issue'}), 404
            
        # Find mechanics who can perform these services
        mechanics = data.get_mechanics()
        suitable_mechanics = []
        
        for mechanic in mechanics:
            # Check if mechanic offers any of the recommended services
            matching_services = [sid for sid in recommended_service_ids if sid in mechanic.services]
            if matching_services:
                # Calculate a match score based on multiple factors
                score = len(matching_services) * 10  # Number of matching services
                score += mechanic.rating * 5         # Higher rating is better
                score += mechanic.experience_years   # More experience is better
                
                # Location matching (if provided)
                if location and location.lower() in mechanic.location.lower():
                    score += 15  # Location bonus
                
                # Get matched service details
                matched_service_details = []
                for sid in matching_services:
                    service = data.get_service_by_id(sid)
                    if service:
                        matched_service_details.append({
                            'id': service.id,
                            'name': service.name,
                            'price': service.price,
                            'duration_minutes': service.duration_minutes,
                            'category': service.category
                        })
                
                # Add specialty services
                specialty_services = mechanic.specialty_services if hasattr(mechanic, 'specialty_services') else []
                
                # Format the response data
                mechanic_data = {
                    'id': mechanic.id,
                    'name': mechanic.name,
                    'specialization': mechanic.specialization,
                    'experience_years': mechanic.experience_years,
                    'rating': mechanic.rating,
                    'review_count': mechanic.review_count,
                    'location': mechanic.location,
                    'profile_image': mechanic.profile_image,
                    'contact': mechanic.phone,
                    'matching_services': matched_service_details,
                    'specialty_services': specialty_services,
                    'match_score': score
                }
                suitable_mechanics.append(mechanic_data)
        
        # Sort by match score, descending
        suitable_mechanics.sort(key=lambda m: m['match_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'mechanics': suitable_mechanics[:5]  # Return top 5 matches
        })
        
    @app.route('/api/find_nearest_mechanics', methods=['POST'])
    def find_nearby_mechanics():
        """API endpoint to find mechanics near a location using maps integration"""
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Not logged in'}), 401
            
        json_data = request.get_json(silent=True) or {}
        latitude = json_data.get('latitude')
        longitude = json_data.get('longitude')
        max_distance = json_data.get('max_distance', 10)  # Default 10km radius
        service_ids = json_data.get('service_ids', [])    # Optional service filtering
        
        if latitude is None or longitude is None:
            return jsonify({'success': False, 'message': 'Location coordinates required'}), 400
            
        # Find nearby mechanics
        nearest_mechanics = utils.find_nearest_mechanics(
            float(latitude), 
            float(longitude), 
            max_distance=float(max_distance),
            service_ids=service_ids if service_ids else None
        )
        
        # Format response
        mechanic_list = []
        for item in nearest_mechanics:
            mechanic = item['mechanic']
            
            # Get all services this mechanic offers
            mechanic_services = []
            for service_id in mechanic.services:
                service = data.get_service_by_id(service_id)
                if service:
                    mechanic_services.append({
                        'id': service.id,
                        'name': service.name,
                        'price': service.price,
                        'category': service.category
                    })
            
            # Format geo location
            geo_location = None
            if mechanic.geo_location:
                geo_location = {
                    'latitude': mechanic.geo_location.latitude,
                    'longitude': mechanic.geo_location.longitude,
                    'address': mechanic.geo_location.address
                }
            
            # Create mechanic data
            mechanic_data = {
                'id': mechanic.id,
                'name': mechanic.name,
                'specialization': mechanic.specialization,
                'experience_years': mechanic.experience_years,
                'rating': mechanic.rating,
                'review_count': mechanic.review_count,
                'location': mechanic.location,
                'profile_image': mechanic.profile_image,
                'phone': mechanic.phone,
                'distance_km': item['distance'],
                'estimated_travel_time_minutes': item['travel_time_estimate'],
                'services': mechanic_services,
                'geo_location': geo_location,
                'specialty_services': mechanic.specialty_services if hasattr(mechanic, 'specialty_services') else []
            }
            mechanic_list.append(mechanic_data)
        
        return jsonify({
            'success': True,
            'mechanics': mechanic_list,
            'total_found': len(mechanic_list)
        })
        
    # Vehicle Marketplace Routes
    @app.route('/marketplace')
    def vehicle_marketplace():
        """Main marketplace page for vehicle listings"""
        form = VehicleSearchForm()
        
        # Get filter parameters from request
        filters = {}
        make = request.args.get('make')
        if make:
            filters['make'] = make
            
        model = request.args.get('model')
        if model:
            filters['model'] = model
            
        min_year = request.args.get('min_year')
        if min_year and min_year.isdigit():
            filters['min_year'] = int(min_year)
            
        max_year = request.args.get('max_year')
        if max_year and max_year.isdigit():
            filters['max_year'] = int(max_year)
            
        min_price = request.args.get('min_price')
        if min_price:
            try:
                filters['min_price'] = float(min_price)
            except ValueError:
                pass
                
        max_price = request.args.get('max_price')
        if max_price:
            try:
                filters['max_price'] = float(max_price)
            except ValueError:
                pass
                
        condition = request.args.get('condition')
        if condition:
            filters['condition'] = condition
        
        # Get vehicle listings with filters
        vehicles = data.get_vehicles_for_sale(filters)
        
        # Pre-populate form with current filter values
        make = request.args.get('make')
        if make:
            form.make.data = make
            
        model = request.args.get('model')
        if model:
            form.model.data = model
            
        min_year = request.args.get('min_year')
        if min_year:
            try:
                form.min_year.data = int(min_year)
            except ValueError:
                pass
                
        max_year = request.args.get('max_year')
        if max_year:
            try:
                form.max_year.data = int(max_year)
            except ValueError:
                pass
                
        min_price = request.args.get('min_price')
        if min_price:
            try:
                form.min_price.data = float(min_price)
            except ValueError:
                pass
                
        max_price = request.args.get('max_price')
        if max_price:
            try:
                form.max_price.data = float(max_price)
            except ValueError:
                pass
                
        condition = request.args.get('condition')
        if condition:
            form.condition.data = condition
        
        return render_template('marketplace.html', 
                              vehicles=vehicles,
                              form=form)
    
    @app.route('/marketplace/vehicle/<int:vehicle_id>')
    def vehicle_listing_detail(vehicle_id):
        """Show detailed page for a specific vehicle listing"""
        vehicle = data.get_vehicle_for_sale_by_id(vehicle_id)
        if not vehicle:
            flash('Vehicle listing not found.', 'danger')
            return redirect(url_for('vehicle_marketplace'))
        
        # Get seller information
        seller = data.get_user_by_id(vehicle.seller_id)
        
        return render_template('vehicle_detail.html', 
                              vehicle=vehicle,
                              seller=seller)
    
    @app.route('/marketplace/my-listings')
    def my_vehicle_listings():
        """View all user's vehicle listings"""
        if 'user_id' not in session:
            flash('Please log in to view your vehicle listings.', 'warning')
            return redirect(url_for('login', next=request.path))
        
        vehicles = data.get_user_vehicle_listings(session['user_id'])
        return render_template('my_listings.html', vehicles=vehicles)
    
    @app.route('/marketplace/create', methods=['GET', 'POST'])
    def create_vehicle_listing():
        """Create a new vehicle listing"""
        if 'user_id' not in session:
            flash('Please log in to create a vehicle listing.', 'warning')
            return redirect(url_for('login', next=request.path))
        
        form = VehicleListingForm()
        
        if form.validate_on_submit():
            # Process features (comma separated string to list)
            features = []
            if form.features.data:
                features = [f.strip() for f in form.features.data.split(',') if f.strip()]
            
            # TODO: Handle image uploads
            images = []
            
            # Create the vehicle listing
            vehicle = data.create_vehicle_listing(
                seller_id=session['user_id'],
                make=form.make.data,
                model=form.model.data,
                year=form.year.data,
                price=form.price.data,
                condition=form.condition.data,
                mileage=form.mileage.data,
                color=form.color.data,
                transmission=form.transmission.data,
                fuel_type=form.fuel_type.data,
                description=form.description.data,
                features=features,
                images=images
            )
            
            flash('Vehicle listing created successfully!', 'success')
            return redirect(url_for('vehicle_listing_detail', vehicle_id=vehicle.id))
        
        return render_template('create_listing.html', form=form)
    
    @app.route('/marketplace/edit/<int:vehicle_id>', methods=['GET', 'POST'])
    def edit_vehicle_listing(vehicle_id):
        """Edit an existing vehicle listing"""
        if 'user_id' not in session:
            flash('Please log in to edit a vehicle listing.', 'warning')
            return redirect(url_for('login', next=request.path))
        
        vehicle = data.get_vehicle_for_sale_by_id(vehicle_id)
        if not vehicle:
            flash('Vehicle listing not found.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        # Verify ownership
        if vehicle.seller_id != session['user_id']:
            flash('You do not have permission to edit this listing.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        form = VehicleListingForm()
        
        if request.method == 'GET':
            # Pre-populate form with current values
            form.make.data = vehicle.make
            form.model.data = vehicle.model
            form.year.data = vehicle.year
            form.price.data = vehicle.price
            form.condition.data = vehicle.condition
            form.mileage.data = vehicle.mileage
            form.color.data = vehicle.color
            form.transmission.data = vehicle.transmission
            form.fuel_type.data = vehicle.fuel_type
            form.description.data = vehicle.description
            form.features.data = ', '.join(vehicle.features)
        
        if form.validate_on_submit():
            # Process features (comma separated string to list)
            features = []
            if form.features.data:
                features = [f.strip() for f in form.features.data.split(',') if f.strip()]
            
            # TODO: Handle image uploads
            
            # Update the vehicle listing
            data.update_vehicle_listing(
                vehicle_id=vehicle_id,
                make=form.make.data,
                model=form.model.data,
                year=form.year.data,
                price=form.price.data,
                condition=form.condition.data,
                mileage=form.mileage.data,
                color=form.color.data,
                transmission=form.transmission.data,
                fuel_type=form.fuel_type.data,
                description=form.description.data,
                features=features
            )
            
            flash('Vehicle listing updated successfully!', 'success')
            return redirect(url_for('vehicle_listing_detail', vehicle_id=vehicle_id))
        
        return render_template('edit_listing.html', form=form, vehicle=vehicle)
    
    @app.route('/marketplace/delete/<int:vehicle_id>', methods=['POST'])
    def delete_vehicle_listing_route():
        """Delete a vehicle listing"""
        if 'user_id' not in session:
            flash('Please log in to delete a vehicle listing.', 'warning')
            return redirect(url_for('login'))
        
        vehicle_id = request.form.get('vehicle_id')
        if not vehicle_id or not vehicle_id.isdigit():
            flash('Invalid vehicle ID.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        vehicle_id = int(vehicle_id)
        vehicle = data.get_vehicle_for_sale_by_id(vehicle_id)
        
        if not vehicle:
            flash('Vehicle listing not found.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        # Verify ownership
        if vehicle.seller_id != session['user_id']:
            flash('You do not have permission to delete this listing.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        # Delete the listing
        data.delete_vehicle_listing(vehicle_id)
        
        flash('Vehicle listing deleted successfully!', 'success')
        return redirect(url_for('my_vehicle_listings'))
    
    @app.route('/marketplace/mark-sold/<int:vehicle_id>', methods=['POST'])
    def mark_vehicle_sold():
        """Mark a vehicle as sold"""
        if 'user_id' not in session:
            flash('Please log in to mark a vehicle as sold.', 'warning')
            return redirect(url_for('login'))
        
        vehicle_id = request.form.get('vehicle_id')
        if not vehicle_id or not vehicle_id.isdigit():
            flash('Invalid vehicle ID.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        vehicle_id = int(vehicle_id)
        vehicle = data.get_vehicle_for_sale_by_id(vehicle_id)
        
        if not vehicle:
            flash('Vehicle listing not found.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        # Verify ownership
        if vehicle.seller_id != session['user_id']:
            flash('You do not have permission to mark this vehicle as sold.', 'danger')
            return redirect(url_for('my_vehicle_listings'))
        
        # Mark as sold
        buyer_id = request.form.get('buyer_id')
        if buyer_id and buyer_id.isdigit():
            data.mark_vehicle_as_sold(vehicle_id, int(buyer_id))
        else:
            data.mark_vehicle_as_sold(vehicle_id)
        
        flash('Vehicle marked as sold successfully!', 'success')
        return redirect(url_for('my_vehicle_listings'))
