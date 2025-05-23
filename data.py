import json
import os
from datetime import datetime, timedelta
from models import Service, Mechanic, User, Vehicle, Booking, TimeSlot, Review, Notification, GeoLocation, Vehicle4Sale
from werkzeug.security import generate_password_hash

# In-memory data storage
services = []
mechanics = []
users = []
vehicles = []
bookings = []
reviews = []
notifications = []
vehicles_for_sale = []

# Initialize with some data
def init_data():
    global services, mechanics, users, vehicles, bookings, reviews, notifications, vehicles_for_sale, service_keywords
    
    # Services
    services = [
        Service(1, "Oil Change", "Standard oil change with filter replacement", 45.99, 30, "Maintenance"),
        Service(2, "Brake Inspection", "Complete brake system inspection and adjustment", 35.00, 45, "Maintenance"),
        Service(3, "Engine Diagnostics", "Computer diagnostics for engine issues", 75.00, 60, "Diagnostics"),
        Service(4, "Tire Rotation", "Rotation of all tires for even wear", 30.00, 30, "Maintenance"),
        Service(5, "Battery Replacement", "Testing and replacement of car battery", 85.00, 45, "Repair"),
        Service(6, "AC Service", "Air conditioning system diagnosis and recharge", 120.00, 90, "Repair"),
        Service(7, "Transmission Fluid Change", "Drain and replace transmission fluid", 110.00, 60, "Maintenance"),
        Service(8, "Wheel Alignment", "Computer-aided alignment of wheels", 90.00, 60, "Repair"),
        Service(9, "Radiator Flush", "Coolant system flush and refill", 75.00, 45, "Maintenance"),
        Service(10, "Headlight Replacement", "Replace headlight bulbs or assemblies", 40.00, 30, "Repair"),
        Service(11, "Brake Pad Replacement", "Replace worn brake pads and inspect rotors", 120.00, 90, "Repair"),
        Service(12, "Spark Plug Replacement", "Remove and replace spark plugs", 95.00, 60, "Maintenance"),
        Service(13, "Suspension Repair", "Diagnosis and repair of suspension components", 150.00, 120, "Repair"),
        Service(14, "Fuel System Cleaning", "Clean fuel injectors and system for improved performance", 85.00, 60, "Maintenance"),
        Service(15, "Starter Replacement", "Remove and replace faulty starter motor", 130.00, 90, "Repair"),
        Service(16, "Alternator Replacement", "Replace failing alternator", 160.00, 90, "Repair"),
        Service(17, "Exhaust System Repair", "Diagnosis and repair of exhaust system leaks or damage", 110.00, 75, "Repair"),
        Service(18, "Power Window Repair", "Fix non-functioning power windows", 95.00, 60, "Repair"),
        Service(19, "Check Engine Light Diagnosis", "Advanced diagnostics for check engine warnings", 85.00, 60, "Diagnostics"),
        Service(20, "Pre-Purchase Inspection", "Comprehensive vehicle inspection before buying", 120.00, 90, "Diagnostics"),
        Service(21, "Car Modifications", "Custom performance upgrades and modifications", 250.00, 180, "Specialty"),
        Service(22, "Key Cutting & Locksmith", "Key replacement, cutting, and electronic key programming", 75.00, 45, "Specialty"),
        Service(23, "Car Restoration", "Classic and vintage car restoration services", 350.00, 240, "Specialty"),
        Service(24, "Vehicle Buying/Selling Assistance", "Professional assistance with vehicle purchases or sales", 150.00, 120, "Consultation"),
    ]
    
    # Create availability schedule
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    default_availability = []
    
    for day in days:
        if day != "Saturday":
            default_availability.append(TimeSlot(day, "08:00", "12:00", True))
            default_availability.append(TimeSlot(day, "13:00", "17:00", True))
        else:
            default_availability.append(TimeSlot(day, "09:00", "13:00", True))
    
    # Mechanics
    mechanics = [
        Mechanic(
            1, "Michael Johnson", "michael@hararemechanics.com", "+263 77 152 2122", 
            "Engine Specialist", 8, 
            "Expert in diagnosing and repairing engine issues with 8 years of experience. Specializes in performance tuning and fuel system optimization.",
            "Harare Central",
            "https://pixabay.com/get/g41825f713016a15af65a97f2d831c387e6635c0e3f755e41bf871505158f7b45bf0e9ae870241ca134405cc24ee87458de469d0e4a6f24eba6610a3957a12a43_1280.jpg",
            4.8, 56, [1, 3, 7, 12, 14, 19, 21], default_availability,
            GeoLocation(-17.8252, 31.0335, "7th Street, Harare Central"),
            ["Performance Tuning", "Engine Rebuilds", "Custom ECU Programming"]
        ),
        Mechanic(
            2, "Grace Moyo", "grace@hararemechanics.com", "+263 78 683 8849",
            "Electrical Systems", 5,
            "Specialized in automotive electrical systems and computer diagnostics. Expert in troubleshooting complex electronic issues.",
            "Avondale, Harare",
            "https://pixabay.com/get/gd9925ae067b218944a0a8142738fcc68fe6a6fde36d9c8b38fe289c91bfc0f9b74b9ce2aeb86a28baec8da299e00ba8783eb34d9d4c5020a049b4436e864604c_1280.jpg",
            4.6, 42, [3, 5, 6, 10, 15, 16, 18, 19, 22], default_availability,
            GeoLocation(-17.7892, 31.0418, "King George Road, Avondale"),
            ["Key Programming", "Security System Installation", "ECU Repairs"]
        ),
        Mechanic(
            3, "David Mapondera", "david@hararemechanics.com", "+263 77 152 2122",
            "Brake & Suspension Specialist", 6,
            "Expert in brake system repairs and suspension work. Certified technician with advanced training in vehicle dynamics.",
            "Borrowdale, Harare",
            "https://pixabay.com/get/g2b44b9419edd576516cb8f0e17729ca8129ffc5de274c74a5c9706796e98e38b6e01197f1864b3d9f092bc0fa577e191cbb67f3637a5066f794e7409840737dc_1280.jpg",
            4.9, 68, [2, 4, 8, 11, 13, 17, 21], default_availability,
            GeoLocation(-17.7318, 31.0918, "Crowhill Road, Borrowdale"),
            ["Coilover Suspension", "Performance Brakes", "Custom Exhaust Systems"]
        ),
        Mechanic(
            4, "Tendai Mutasa", "tendai@hararemechanics.com", "+263 78 683 8849",
            "General Mechanic & Vehicle Inspector", 10,
            "All-round mechanic with 10 years of experience in all aspects of car repair. Provides comprehensive vehicle inspection and maintenance services.",
            "Eastlea, Harare",
            "https://pixabay.com/get/g53f14e50f6526b37eecfda5e5e855bc2006f9ce27e3d789387c3cf752c7697aa1c1ede670fcbae8090960a5775105104a174737c87830e830f746e4a4f77c342_1280.jpg",
            4.7, 89, [1, 2, 4, 7, 9, 20, 24], default_availability,
            GeoLocation(-17.8102, 31.0833, "Samora Machel Avenue, Eastlea"),
            ["Vehicle Appraisal", "Pre-Purchase Inspection", "Fleet Maintenance"]
        ),
        Mechanic(
            5, "Chiedza Mupita", "chiedza@hararemechanics.com", "+263 77 152 2122",
            "Transmission & Restoration Specialist", 7,
            "Specializes in manual and automatic transmission repairs and classic car restoration. Expert in diagnosing complex drivetrain issues.",
            "Mabelreign, Harare",
            "https://pixabay.com/get/g20ef4ebfa2a1456a2a21e5522f5db72dd7f9a3c9c4c9fe4b63d3c25ff8e50a7a0bd02a2a72db0f57195fd99d2398c35eb5f6c1d8ffd6abfc3aeb48f52afee5dc_1280.jpg",
            4.7, 45, [3, 7, 12, 15, 16, 19, 23], default_availability,
            GeoLocation(-17.7833, 31.0167, "Sherwood Drive, Mabelreign"),
            ["Classic Car Restoration", "Vintage Engine Rebuilds", "Custom Interiors"]
        )
    ]
    
    # Users
    users = [
        User(1, "Test Customer", "customer@example.com", "+263771234567", 
             generate_password_hash("password123"), False, None),
        User(2, "Michael Johnson", "michael@hararemechanics.com", "+263775123456", 
             generate_password_hash("mechanic123"), True, 1),
        User(3, "Grace Moyo", "grace@hararemechanics.com", "+263775234567", 
             generate_password_hash("mechanic123"), True, 2),
        User(4, "David Mapondera", "david@hararemechanics.com", "+263775345678", 
             generate_password_hash("mechanic123"), True, 3),
        User(5, "Tendai Mutasa", "tendai@hararemechanics.com", "+263775456789", 
             generate_password_hash("mechanic123"), True, 4),
        User(6, "Chiedza Mupita", "chiedza@hararemechanics.com", "+263775567890", 
             generate_password_hash("mechanic123"), True, 5)
    ]
    
    # Vehicles
    vehicles = [
        Vehicle(1, 1, "Toyota", "Corolla", 2018, "ABC123"),
        Vehicle(2, 1, "Honda", "Civic", 2015, "XYZ789")
    ]
    
    # Generate some sample bookings for the test customer
    current_date = datetime.now()
    
    # One past booking
    past_date = (current_date - timedelta(days=7)).strftime('%Y-%m-%d')
    bookings.append(
        Booking(
            id=1,
            customer_id=1,
            mechanic_id=1,
            service_id=1,
            vehicle_id=1,
            booking_date=past_date,
            booking_time="10:00",
            status="Completed",
            issue_description="Regular oil change service.",
            created_at=(current_date - timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S'),
            customer_name="Test Customer",
            mechanic_name="Michael Johnson",
            service_name="Oil Change",
            vehicle_details="Toyota Corolla (2018)"
        )
    )
    
    # One upcoming booking
    future_date = (current_date + timedelta(days=3)).strftime('%Y-%m-%d')
    bookings.append(
        Booking(
            id=2,
            customer_id=1,
            mechanic_id=2, 
            service_id=3,
            vehicle_id=1,
            booking_date=future_date,
            booking_time="14:00",
            status="Confirmed",
            issue_description="Check engine light is on, need diagnostics.",
            created_at=current_date.strftime('%Y-%m-%d %H:%M:%S'),
            customer_name="Test Customer",
            mechanic_name="Grace Moyo",
            service_name="Engine Diagnostics",
            vehicle_details="Toyota Corolla (2018)"
        )
    )

# Data access functions
def get_services():
    return services

def get_service_by_id(service_id):
    return next((s for s in services if s.id == service_id), None)

def get_mechanics():
    return mechanics

def get_mechanic_by_id(mechanic_id):
    return next((m for m in mechanics if m.id == mechanic_id), None)

def get_mechanic_services(mechanic_id):
    mechanic = get_mechanic_by_id(mechanic_id)
    if not mechanic:
        return []
    return [s for s in services if s.id in mechanic.services]

def get_user_by_email(email):
    return next((u for u in users if u.email == email), None)

def get_user_by_id(user_id):
    return next((u for u in users if u.id == user_id), None)
    
def get_user_by_mechanic_id(mechanic_id):
    """Get user account associated with a mechanic"""
    return next((u for u in users if u.is_mechanic and u.mechanic_id == mechanic_id), None)

def register_user(name, email, phone, password, is_mechanic=False):
    if get_user_by_email(email):
        return None
    
    user_id = max([u.id for u in users], default=0) + 1
    password_hash = generate_password_hash(password)
    
    new_user = User(
        id=user_id,
        name=name,
        email=email,
        phone=phone,
        password_hash=password_hash,
        is_mechanic=is_mechanic
    )
    
    users.append(new_user)
    return new_user

def get_vehicles_by_user(user_id):
    return [v for v in vehicles if v.user_id == user_id]

def get_vehicle_by_id(vehicle_id):
    return next((v for v in vehicles if v.id == vehicle_id), None)

def add_vehicle(user_id, make, model, year, license_plate):
    vehicle_id = max([v.id for v in vehicles], default=0) + 1
    
    new_vehicle = Vehicle(
        id=vehicle_id,
        user_id=user_id,
        make=make,
        model=model,
        year=year,
        license_plate=license_plate
    )
    
    vehicles.append(new_vehicle)
    return new_vehicle

def get_bookings_by_customer(customer_id):
    customer_bookings = [b for b in bookings if b.customer_id == customer_id]
    
    # Enrich booking data
    for booking in customer_bookings:
        mechanic = get_mechanic_by_id(booking.mechanic_id)
        service = get_service_by_id(booking.service_id)
        vehicle = get_vehicle_by_id(booking.vehicle_id)
        
        if mechanic and not booking.mechanic_name:
            booking.mechanic_name = mechanic.name
        
        if service and not booking.service_name:
            booking.service_name = service.name
            
        if vehicle and not booking.vehicle_details:
            booking.vehicle_details = f"{vehicle.make} {vehicle.model} ({vehicle.year})"
    
    return customer_bookings

def get_bookings_by_mechanic(mechanic_id):
    mechanic_bookings = [b for b in bookings if b.mechanic_id == mechanic_id]
    
    # Enrich booking data
    for booking in mechanic_bookings:
        user = get_user_by_id(booking.customer_id)
        service = get_service_by_id(booking.service_id)
        vehicle = get_vehicle_by_id(booking.vehicle_id)
        
        if user and not booking.customer_name:
            booking.customer_name = user.name
        
        if service and not booking.service_name:
            booking.service_name = service.name
            
        if vehicle and not booking.vehicle_details:
            booking.vehicle_details = f"{vehicle.make} {vehicle.model} ({vehicle.year})"
    
    return mechanic_bookings

def create_booking(customer_id, mechanic_id, service_id, vehicle_id, booking_date, 
                  booking_time, issue_description):
    booking_id = max([b.id for b in bookings], default=0) + 1
    
    # Get related objects to enrich the booking
    customer = get_user_by_id(customer_id)
    mechanic = get_mechanic_by_id(mechanic_id)
    service = get_service_by_id(service_id)
    vehicle = get_vehicle_by_id(vehicle_id)
    
    customer_name = customer.name if customer else ""
    mechanic_name = mechanic.name if mechanic else ""
    service_name = service.name if service else ""
    vehicle_details = f"{vehicle.make} {vehicle.model} ({vehicle.year})" if vehicle else ""
    
    new_booking = Booking(
        id=booking_id,
        customer_id=customer_id,
        mechanic_id=mechanic_id,
        service_id=service_id,
        vehicle_id=vehicle_id,
        booking_date=booking_date,
        booking_time=booking_time,
        status="Pending",
        issue_description=issue_description,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        customer_name=customer_name,
        mechanic_name=mechanic_name,
        service_name=service_name,
        vehicle_details=vehicle_details,
        has_review=False
    )
    
    bookings.append(new_booking)
    
    # Create notifications for new booking
    # Notification for customer
    create_notification(
        customer_id,
        "Booking Submitted",
        f"Your booking request for {service_name} with {mechanic_name} on {booking_date} has been submitted.",
        "booking",
        booking_id
    )
    
    # Notification for mechanic
    mechanic_user = get_user_by_mechanic_id(mechanic_id)
    if mechanic_user:
        create_notification(
            mechanic_user.id,
            "New Booking Request",
            f"{customer_name} has requested your services for {service_name} on {booking_date} at {booking_time}.",
            "booking",
            booking_id
        )
    
    return new_booking

def update_booking_status(booking_id, new_status):
    booking = next((b for b in bookings if b.id == booking_id), None)
    if booking:
        old_status = booking.status
        booking.status = new_status
        
        # Create notifications for status changes
        if old_status != new_status:
            # Notify the customer
            create_booking_notification(booking.customer_id, booking)
            
            # Notify the mechanic if applicable
            if booking.mechanic_id:
                create_booking_notification(booking.mechanic_id, booking, is_mechanic=True)
                
        return booking
    return None

def get_reviews_by_mechanic(mechanic_id):
    """Get all reviews for a specific mechanic"""
    return [r for r in reviews if r.mechanic_id == mechanic_id]

def get_review_by_booking(booking_id):
    """Get the review for a specific booking if it exists"""
    return next((r for r in reviews if r.booking_id == booking_id), None)

def create_review(booking_id, customer_id, mechanic_id, rating, comment):
    """Create a new review for a completed booking"""
    # Validate that this booking exists, is completed, and belongs to this customer
    booking = next((b for b in bookings if b.id == booking_id and 
                   b.customer_id == customer_id and 
                   b.status == "Completed"), None)
    
    if not booking:
        return None
    
    # Check if this booking already has a review
    existing_review = get_review_by_booking(booking_id)
    if existing_review:
        return None
    
    # Create the review
    review_id = max([r.id for r in reviews], default=0) + 1
    customer = get_user_by_id(customer_id)
    customer_name = customer.name if customer else ""
    
    new_review = Review(
        id=review_id,
        booking_id=booking_id,
        customer_id=customer_id,
        mechanic_id=mechanic_id,
        rating=rating,
        comment=comment,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        customer_name=customer_name
    )
    
    reviews.append(new_review)
    
    # Mark the booking as having a review
    booking.has_review = True
    
    # Update mechanic's rating
    update_mechanic_rating(mechanic_id)
    
    return new_review

def update_mechanic_rating(mechanic_id):
    """Update a mechanic's overall rating based on all their reviews"""
    mechanic = get_mechanic_by_id(mechanic_id)
    if not mechanic:
        return
    
    mechanic_reviews = get_reviews_by_mechanic(mechanic_id)
    if not mechanic_reviews:
        return
    
    # Calculate new average rating
    total_rating = sum(review.rating for review in mechanic_reviews)
    avg_rating = round(total_rating / len(mechanic_reviews), 1)
    
    # Update mechanic's rating and review count
    mechanic.rating = avg_rating
    mechanic.review_count = len(mechanic_reviews)

# Notification functions
def get_notifications_by_user(user_id):
    """Get all notifications for a specific user"""
    return [n for n in notifications if n.user_id == user_id and not n.is_read]

def mark_notification_read(notification_id):
    """Mark a notification as read"""
    notification = next((n for n in notifications if n.id == notification_id), None)
    if notification:
        notification.is_read = True
        return True
    return False

def create_notification(user_id, title, message, notification_type, related_id=0):
    """Create a new notification for a user"""
    notification_id = max([n.id for n in notifications], default=0) + 1
    
    new_notification = Notification(
        id=notification_id,
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_id=related_id,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        is_read=False
    )
    
    notifications.append(new_notification)
    return new_notification

def create_booking_notification(user_id, booking, is_mechanic=False):
    """Create a notification related to a booking status change"""
    if not booking:
        return None
        
    # Get related entities
    service = get_service_by_id(booking.service_id)
    service_name = service.name if service else "Service"
    
    if is_mechanic:
        customer = get_user_by_id(booking.customer_id)
        customer_name = customer.name if customer else "A customer"
        
        if booking.status == "Pending":
            title = "New Booking Request"
            message = f"{customer_name} has requested your services for {service_name} on {booking.booking_date} at {booking.booking_time}."
        elif booking.status == "Confirmed":
            title = "Booking Confirmed"
            message = f"You have confirmed the booking for {service_name} with {customer_name} on {booking.booking_date} at {booking.booking_time}."
        elif booking.status == "Completed":
            title = "Booking Marked as Completed"
            message = f"You have marked the {service_name} for {customer_name} as completed."
        elif booking.status == "Cancelled":
            title = "Booking Cancelled"
            message = f"The booking for {service_name} with {customer_name} on {booking.booking_date} has been cancelled."
        else:
            title = "Booking Update"
            message = f"The status of the booking with {customer_name} has been updated to {booking.status}."
    else:
        mechanic = get_mechanic_by_id(booking.mechanic_id)
        mechanic_name = mechanic.name if mechanic else "The mechanic"
        
        if booking.status == "Pending":
            title = "Booking Submitted"
            message = f"Your booking request for {service_name} with {mechanic_name} on {booking.booking_date} has been submitted."
        elif booking.status == "Confirmed":
            title = "Booking Confirmed"
            message = f"{mechanic_name} has confirmed your booking for {service_name} on {booking.booking_date} at {booking.booking_time}."
        elif booking.status == "Completed":
            title = f"Booking Completed - Rate {mechanic_name}"
            message = f"Your booking with {mechanic_name} for {service_name} has been marked as completed. Would you like to leave a review?"
        elif booking.status == "Cancelled":
            title = "Booking Cancelled"
            message = f"Your booking for {service_name} with {mechanic_name} on {booking.booking_date} has been cancelled."
        else:
            title = "Booking Update"
            message = f"The status of your booking with {mechanic_name} has been updated to {booking.status}."
    
    return create_notification(user_id, title, message, "booking", booking.id)

# Service recommendation system - maps issue keywords to service IDs
service_keywords = {
    # Engine related
    "engine": [3, 19],  # Engine Diagnostics, Check Engine Light
    "light": [10, 19],  # Headlight Replacement, Check Engine Light
    "check engine": [19],  # Check Engine Light
    "warning": [19],  # Check Engine Light
    "performance": [3, 14],  # Engine Diagnostics, Fuel System Cleaning
    "slow": [3, 14],  # Engine Diagnostics, Fuel System Cleaning
    "stalling": [3, 15],  # Engine Diagnostics, Starter Replacement
    
    # Maintenance
    "oil": [1],  # Oil Change 
    "maintenance": [1, 4, 7, 9, 12],  # Various maintenance services
    "regular": [1, 4, 7, 9, 12],  # Various maintenance services
    "fluid": [1, 7, 9],  # Oil Change, Transmission Fluid, Radiator Flush
    
    # Brakes
    "brake": [2, 11],  # Brake Inspection, Brake Pad Replacement
    "stopping": [2, 11],  # Brake-related issues
    "squeaking": [2, 11, 13],  # Brake or suspension issues
    "grinding": [2, 11],  # Brake issues
    
    # Tires and alignment
    "tire": [4],  # Tire Rotation
    "alignment": [8],  # Wheel Alignment
    "pulling": [8],  # Wheel Alignment issues
    "vibration": [8, 13],  # Wheel Alignment, Suspension issues
    
    # Air conditioning
    "ac": [6],  # AC Service
    "air": [6],  # AC Service
    "cold": [6],  # AC Service
    "hot": [6, 9],  # AC Service, Radiator Flush
    "cooling": [9],  # Radiator Flush
    
    # Electrical
    "battery": [5],  # Battery Replacement
    "start": [5, 15],  # Battery or Starter issues
    "power": [5, 18],  # Battery, Power Window issues
    "electric": [5, 16, 18],  # Electrical issues
    "window": [18],  # Power Window Repair
    "alternator": [16],  # Alternator Replacement
    "charging": [16],  # Alternator issues
    
    # Transmission
    "transmission": [7],  # Transmission Fluid Change
    "gear": [7],  # Transmission issues
    "shifting": [7],  # Transmission issues
    
    # Exhaust
    "exhaust": [17],  # Exhaust System Repair
    "smoke": [17, 3],  # Exhaust issues or Engine Diagnostics
    "loud": [17],  # Exhaust issues
    
    # General
    "noise": [3, 13, 17],  # Various potential issues
    "leak": [1, 7, 9, 17],  # Various fluid leaks
    "inspection": [2, 20],  # Brake Inspection or Pre-Purchase
    "buying": [20],  # Pre-Purchase Inspection
    "new car": [20],  # Pre-Purchase Inspection
    "used car": [20],  # Pre-Purchase Inspection
    
    # Car Modifications
    "modification": [21],  # Car Modifications
    "mod": [21],  # Car Modifications
    "custom": [21],  # Car Modifications
    "tuning": [21],  # Car Modifications
    "upgrade": [21],  # Car Modifications
    
    # Key Cutting/Locksmith Services
    "key": [22],  # Key Cutting
    "lock": [22],  # Key Cutting/Locksmith
    "unlock": [22],  # Locksmith
    "remote": [22],  # Key fob/remote programming
    
    # Car Restoration
    "restoration": [23],  # Car Restoration
    "restore": [23],  # Car Restoration
    "classic": [23],  # Classic Car Restoration
    "vintage": [23],  # Vintage Car Restoration
    "rebuild": [23],  # Car Restoration
    
    # Car Buying/Selling Assistance
    "sell": [24],  # Car Selling Assistance
    "buy": [24],  # Car Buying Assistance
    "purchase": [24],  # Car Buying Assistance
    "value": [24],  # Car Valuation
    "appraisal": [24]  # Car Appraisal
}

def update_user_profile(user_id, name, phone, bio=None):
    """Update a user's profile information"""
    user = get_user_by_id(user_id)
    if not user:
        return False
        
    user.name = name
    user.phone = phone
    if bio is not None:
        user.bio = bio
            
    return True
    
def update_user_password(user_id, new_password):
    """Update a user's password"""
    from werkzeug.security import generate_password_hash
    
    user = get_user_by_id(user_id)
    if not user:
        return False
        
    user.password_hash = generate_password_hash(new_password)
    return True
    
def recommend_services(issue_description):
    """
    Analyze issue description and recommend appropriate services
    Returns a list of service IDs sorted by relevance
    """
    if not issue_description:
        return []
        
    # Convert to lowercase for case-insensitive matching
    issue_text = issue_description.lower()
    
    # Track matched services and their relevance score
    service_matches = {}
    
    for keyword, service_ids in service_keywords.items():
        if keyword in issue_text:
            # How relevant is this keyword (based on length - longer keywords are more specific)
            relevance = len(keyword)
            
            for service_id in service_ids:
                if service_id in service_matches:
                    service_matches[service_id] += relevance
                else:
                    service_matches[service_id] = relevance
    
    # Sort services by relevance score (descending)
    recommended_services = sorted(service_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Return just the service IDs, in order of relevance
    return [service_id for service_id, score in recommended_services]

# Functions for vehicle marketplace (car buying/selling)
def get_vehicles_for_sale(filters=None):
    """
    Get all vehicles for sale, with optional filtering
    
    filters: dict with optional keys:
        - make: filter by vehicle make
        - model: filter by vehicle model
        - min_year: minimum vehicle year
        - max_year: maximum vehicle year
        - min_price: minimum price
        - max_price: maximum price
        - condition: vehicle condition
    """
    filtered_vehicles = vehicles_for_sale.copy()
    
    if not filters:
        return filtered_vehicles
        
    # Apply filters
    if 'make' in filters and filters['make']:
        filtered_vehicles = [v for v in filtered_vehicles if v.make.lower() == filters['make'].lower()]
        
    if 'model' in filters and filters['model']:
        filtered_vehicles = [v for v in filtered_vehicles if v.model.lower() == filters['model'].lower()]
        
    if 'min_year' in filters and filters['min_year']:
        filtered_vehicles = [v for v in filtered_vehicles if v.year >= int(filters['min_year'])]
        
    if 'max_year' in filters and filters['max_year']:
        filtered_vehicles = [v for v in filtered_vehicles if v.year <= int(filters['max_year'])]
        
    if 'min_price' in filters and filters['min_price']:
        filtered_vehicles = [v for v in filtered_vehicles if v.price >= float(filters['min_price'])]
        
    if 'max_price' in filters and filters['max_price']:
        filtered_vehicles = [v for v in filtered_vehicles if v.price <= float(filters['max_price'])]
        
    if 'condition' in filters and filters['condition']:
        filtered_vehicles = [v for v in filtered_vehicles if v.condition.lower() == filters['condition'].lower()]
        
    # By default, only show unsold vehicles
    if 'show_sold' not in filters or not filters['show_sold']:
        filtered_vehicles = [v for v in filtered_vehicles if not v.is_sold]
        
    return filtered_vehicles

def get_vehicle_for_sale_by_id(vehicle_id):
    """Get a vehicle listing by ID"""
    return next((v for v in vehicles_for_sale if v.id == vehicle_id), None)

def get_user_vehicle_listings(user_id):
    """Get all vehicle listings for a specific user"""
    return [v for v in vehicles_for_sale if v.seller_id == user_id]

def create_vehicle_listing(seller_id, make, model, year, price, condition, mileage, color, 
                           transmission, fuel_type, description, features=None, images=None):
    """Create a new vehicle listing"""
    # Generate a new ID
    vehicle_id = max([v.id for v in vehicles_for_sale], default=0) + 1
    
    # Create the vehicle listing
    new_listing = Vehicle4Sale(
        id=vehicle_id,
        seller_id=seller_id,
        make=make,
        model=model,
        year=year,
        price=price,
        condition=condition,
        mileage=mileage,
        color=color,
        transmission=transmission,
        fuel_type=fuel_type,
        description=description,
        features=features or [],
        images=images or [],
        listing_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        is_sold=False
    )
    
    vehicles_for_sale.append(new_listing)
    
    # Notify the seller
    create_notification(
        user_id=seller_id,
        title="Vehicle Listing Created",
        message=f"Your listing for {make} {model} ({year}) has been created successfully.",
        notification_type="marketplace",
        related_id=vehicle_id
    )
    
    return new_listing

def update_vehicle_listing(vehicle_id, **kwargs):
    """Update an existing vehicle listing"""
    vehicle = get_vehicle_for_sale_by_id(vehicle_id)
    if not vehicle:
        return None
        
    # Update fields
    for key, value in kwargs.items():
        if hasattr(vehicle, key):
            setattr(vehicle, key, value)
            
    return vehicle

def mark_vehicle_as_sold(vehicle_id, buyer_id=None):
    """Mark a vehicle as sold"""
    vehicle = get_vehicle_for_sale_by_id(vehicle_id)
    if not vehicle:
        return None
        
    vehicle.is_sold = True
    
    # Notify the seller
    create_notification(
        user_id=vehicle.seller_id,
        title="Vehicle Marked as Sold",
        message=f"Your {vehicle.make} {vehicle.model} ({vehicle.year}) has been marked as sold.",
        notification_type="marketplace",
        related_id=vehicle_id
    )
    
    # Notify the buyer if provided
    if buyer_id:
        create_notification(
            user_id=buyer_id,
            title="Vehicle Purchase Recorded",
            message=f"Your purchase of {vehicle.make} {vehicle.model} ({vehicle.year}) has been recorded.",
            notification_type="marketplace",
            related_id=vehicle_id
        )
        
    return vehicle

def delete_vehicle_listing(vehicle_id):
    """Delete a vehicle listing"""
    vehicle = get_vehicle_for_sale_by_id(vehicle_id)
    if not vehicle:
        return False
        
    vehicles_for_sale.remove(vehicle)
    return True

# Initialize data when this module is imported
init_data()
