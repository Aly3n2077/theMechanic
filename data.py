import json
import os
from datetime import datetime, timedelta
from models import Service, Mechanic, User, Vehicle, Booking, TimeSlot
from werkzeug.security import generate_password_hash

# In-memory data storage
services = []
mechanics = []
users = []
vehicles = []
bookings = []

# Initialize with some data
def init_data():
    global services, mechanics, users, vehicles, bookings
    
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
            1, "Michael Johnson", "michael@hararemechanics.com", "+263775123456", 
            "Engine Specialist", 8, 
            "Expert in diagnosing and repairing engine issues with 8 years of experience.",
            "Harare Central",
            "https://pixabay.com/get/g41825f713016a15af65a97f2d831c387e6635c0e3f755e41bf871505158f7b45bf0e9ae870241ca134405cc24ee87458de469d0e4a6f24eba6610a3957a12a43_1280.jpg",
            4.8, 56, [1, 3, 7], default_availability
        ),
        Mechanic(
            2, "Grace Moyo", "grace@hararemechanics.com", "+263775234567",
            "Electrical Systems", 5,
            "Specialized in automotive electrical systems and computer diagnostics.",
            "Avondale, Harare",
            "https://pixabay.com/get/gd9925ae067b218944a0a8142738fcc68fe6a6fde36d9c8b38fe289c91bfc0f9b74b9ce2aeb86a28baec8da299e00ba8783eb34d9d4c5020a049b4436e864604c_1280.jpg",
            4.6, 42, [3, 5, 6, 10], default_availability
        ),
        Mechanic(
            3, "David Mapondera", "david@hararemechanics.com", "+263775345678",
            "Brake Specialist", 6,
            "Expert in brake system repairs and maintenance. Certified technician.",
            "Borrowdale, Harare",
            "https://pixabay.com/get/g2b44b9419edd576516cb8f0e17729ca8129ffc5de274c74a5c9706796e98e38b6e01197f1864b3d9f092bc0fa577e191cbb67f3637a5066f794e7409840737dc_1280.jpg",
            4.9, 68, [2, 4, 8], default_availability
        ),
        Mechanic(
            4, "Tendai Mutasa", "tendai@hararemechanics.com", "+263775456789",
            "General Mechanic", 10,
            "All-round mechanic with 10 years of experience in all aspects of car repair.",
            "Eastlea, Harare",
            "https://pixabay.com/get/g53f14e50f6526b37eecfda5e5e855bc2006f9ce27e3d789387c3cf752c7697aa1c1ede670fcbae8090960a5775105104a174737c87830e830f746e4a4f77c342_1280.jpg",
            4.7, 89, [1, 2, 4, 7, 9], default_availability
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
             generate_password_hash("mechanic123"), True, 4)
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
        vehicle_details=vehicle_details
    )
    
    bookings.append(new_booking)
    return new_booking

def update_booking_status(booking_id, new_status):
    booking = next((b for b in bookings if b.id == booking_id), None)
    if booking:
        booking.status = new_status
        return booking
    return None

# Initialize data when this module is imported
init_data()
