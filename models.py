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
class GeoLocation:
    latitude: float
    longitude: float
    address: str = ""
    
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
    geo_location: Optional[GeoLocation] = None
    specialty_services: List[str] = field(default_factory=list)

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
    has_review: bool = False
    
@dataclass
class Review:
    id: int
    booking_id: int
    customer_id: int
    mechanic_id: int
    rating: float  # 1-5 star rating
    comment: str
    created_at: str
    customer_name: str = ""
    
@dataclass
class Notification:
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str  # booking, reminder, promo, system
    related_id: int = 0  # ID of related item (booking, etc)
    created_at: str = ""
    is_read: bool = False
    
@dataclass
class Vehicle4Sale:
    id: int
    seller_id: int
    make: str
    model: str
    year: int
    price: float
    condition: str  # New, Used, Certified Pre-Owned
    mileage: int
    color: str
    transmission: str
    fuel_type: str
    description: str
    features: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    listing_date: str = ""
    is_sold: bool = False
