from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, time

@dataclass
class Service:
    id: int
    name: str
    description: str
    price: float
    duration_minutes: int
    category: str

@dataclass
class TimeSlot:
    day: str
    start_time: str
    end_time: str
    available: bool = True
    
@dataclass
class Mechanic:
    id: int
    name: str
    email: str
    phone: str
    specialization: str
    experience_years: int
    bio: str
    location: str
    profile_image: str
    rating: float
    review_count: int
    services: List[int] = field(default_factory=list)
    availability: List[TimeSlot] = field(default_factory=list)

@dataclass
class User:
    id: int
    name: str
    email: str
    phone: str
    password_hash: str
    is_mechanic: bool = False
    mechanic_id: Optional[int] = None

@dataclass
class Vehicle:
    id: int
    user_id: int
    make: str
    model: str
    year: int
    license_plate: str
    
@dataclass
class Booking:
    id: int
    customer_id: int
    mechanic_id: int
    service_id: int
    vehicle_id: int
    booking_date: str
    booking_time: str
    status: str  # Pending, Confirmed, Completed, Cancelled
    issue_description: str
    created_at: str
    customer_name: str = ""
    mechanic_name: str = ""
    service_name: str = ""
    vehicle_details: str = ""
