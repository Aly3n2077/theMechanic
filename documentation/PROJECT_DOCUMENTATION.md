# Harare Mobile Mechanics - Project Documentation

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Data Models](#data-models)
3. [Core Components](#core-components)
4. [Feature Documentation](#feature-documentation)
5. [API Endpoints](#api-endpoints)
6. [User Flows](#user-flows)
7. [Changelog](#changelog)

## System Architecture

Harare Mobile Mechanics follows a Flask-based web application architecture with the following components:

### Frontend
- **Templates**: Jinja2 templating engine with HTML5
- **Styling**: Bootstrap 5 with custom CSS
- **JavaScript**: Vanilla JS with minimal dependencies

### Backend
- **Framework**: Flask (Python)
- **Data Storage**: In-memory for development, PostgreSQL for production
- **Authentication**: Session-based authentication
- **Form Handling**: Flask-WTF for form validation

### System Components Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser   │────▶│ Flask Routes │────▶│  Data Layer  │
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                    │                    │
       │                    ▼                    ▼
       │             ┌──────────────┐     ┌──────────────┐
       └─────────────│   Templates  │     │  Data Models │
                     └──────────────┘     └──────────────┘
```

## Data Models

The application uses the following core data models:

### User
Represents customers and mechanics registered in the system.

```python
@dataclass
class User:
    id: int
    name: str
    email: str
    phone: str
    password_hash: str
    is_mechanic: bool = False
    mechanic_id: Optional[int] = None
    bio: str = ""
```

### Mechanic
Represents service providers with their specializations and availability.

```python
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
```

### Service
Defines the services offered by mechanics.

```python
@dataclass
class Service:
    id: int
    name: str
    description: str
    price: float
    duration_minutes: int
    category: str
```

### Vehicle
Customer-owned vehicles that receive service.

```python
@dataclass
class Vehicle:
    id: int
    user_id: int
    make: str
    model: str
    year: int
    license_plate: str
```

### Vehicle4Sale
Vehicles listed for sale in the marketplace.

```python
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
```

### Booking
Service appointments between customers and mechanics.

```python
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
```

### Review
Customer feedback on mechanics after service completion.

```python
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
```

### Notification
System messages for users.

```python
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
```

## Core Components

### data.py
Contains all data-related functions and business logic for the application:
- User management (registration, authentication)
- Booking management
- Service recommendations
- Review system
- Notification system
- Vehicle marketplace functionality

### routes.py
Defines all application routes and handles HTTP requests:
- User authentication routes
- Dashboard routes
- Booking workflow
- Vehicle management
- Marketplace routes
- Profile management

### forms.py
Contains form definitions using Flask-WTF:
- Login and registration forms
- Booking forms
- Vehicle management forms
- Review forms
- Vehicle listing forms
- Profile editing forms

### utils.py
Utility functions for:
- Date/time handling
- Authentication helpers
- Geolocation calculations
- Time slot management
- Booking validation

### models.py
Defines dataclasses for all application models.

## Feature Documentation

### User Authentication

The platform supports user registration and authentication with two types of users:
- **Customers**: Regular users who can book mechanics
- **Mechanics**: Service providers who can be booked by customers

Authentication is session-based, with passwords securely hashed using Werkzeug's `generate_password_hash`.

### Mechanic Booking System

The booking process follows these steps:
1. User selects a mechanic based on expertise and ratings
2. User selects a service and vehicle
3. User chooses available date and time slot
4. User provides issue description
5. System creates booking and notifies the mechanic
6. Mechanic accepts or reschedules the booking
7. Service is performed at the scheduled time
8. User can review the mechanic after service completion

### Service Recommendation Engine

The platform includes an intelligent recommendation system that analyzes user's issue description to suggest appropriate services:

1. User describes their automotive issue
2. System analyzes the description using keyword matching
3. System returns a ranked list of recommended services

```python
def recommend_services(issue_description):
    """
    Analyze issue description and recommend appropriate services
    Returns a list of service IDs sorted by relevance
    """
    # Implementation details...
```

### Mechanic Rating System

After service completion, customers can rate mechanics based on:
- Overall satisfaction (1-5 stars)
- Written feedback

The system automatically updates mechanic's average rating and review count.

### Notification System

The platform includes a notification system to keep users informed about:
- Booking status changes
- New reviews
- System announcements
- Marketplace activity

### Vehicle Marketplace

The vehicle marketplace allows users to:
- List vehicles for sale with detailed information
- Browse and search available vehicles
- Filter by make, model, year, price, etc.
- Contact sellers directly
- Mark vehicles as sold

## API Endpoints

### User Authentication
- `POST /login`: User login
- `POST /register`: User registration
- `GET /logout`: User logout

### Mechanic Booking
- `GET /mechanics`: List all mechanics
- `GET /mechanics/<id>`: Get mechanic details
- `GET /book/<mechanic_id>`: Book a mechanic
- `POST /book/<mechanic_id>`: Submit booking request
- `GET /booking/confirmation/<booking_id>`: Booking confirmation

### User Dashboard
- `GET /dashboard`: User dashboard
- `GET /dashboard/customer`: Customer dashboard
- `GET /dashboard/mechanic`: Mechanic dashboard

### Vehicle Management
- `GET /vehicles/add`: Add vehicle form
- `POST /vehicles/add`: Add vehicle submission

### Review System
- `GET /review/<booking_id>`: Review form
- `POST /review/<booking_id>`: Submit review

### Marketplace
- `GET /marketplace`: Browse vehicle listings
- `GET /marketplace/vehicle/<id>`: Vehicle listing details
- `GET /marketplace/create`: Create listing form
- `POST /marketplace/create`: Submit listing
- `GET /marketplace/edit/<id>`: Edit listing form
- `POST /marketplace/edit/<id>`: Update listing
- `POST /marketplace/delete/<id>`: Delete listing
- `POST /marketplace/mark-sold/<id>`: Mark vehicle as sold

### Profile Management
- `GET /profile/edit`: Edit profile form
- `POST /profile/edit`: Update profile

## User Flows

### Customer Registration and Booking
1. User registers an account
2. User adds a vehicle to their profile
3. User browses available mechanics
4. User selects a mechanic based on expertise and reviews
5. User books a service, selecting time and providing issue details
6. User receives confirmation and awaits service
7. After service, user can leave a review

### Mechanic Registration and Service
1. Mechanic registers as a service provider
2. Mechanic sets availability and services offered
3. Mechanic receives booking notifications
4. Mechanic accepts or reschedules bookings
5. Mechanic performs service at scheduled time
6. Mechanic marks booking as completed

### Vehicle Marketplace
1. Seller creates account or logs in
2. Seller creates vehicle listing with details and photos
3. Buyer browses and searches for vehicles
4. Buyer views detailed listing and contacts seller
5. Once sold, seller marks vehicle as sold

## Changelog

### Version 1.0.0 (May 19, 2025)
- Initial platform launch with core functionality:
  - User registration and authentication
  - Mechanic profiles and booking system
  - Customer dashboard for booking management
  - Vehicle management for customers
  - Review and rating system
  - Basic notification system

### Version 1.1.0 (May 19, 2025)
- Added Vehicle Marketplace:
  - Vehicle listing functionality
  - Search and filtering capabilities
  - Seller dashboard
  - Communication features between buyers and sellers

### Version 1.2.0 (May 19, 2025)
- Enhanced User Profiles:
  - Profile editing functionality
  - Bio and additional user information
  - Password change capability
  - Improved user dashboard

### Version 1.3.0 (May 19, 2025)
- Added Service Recommendation Engine:
  - Intelligent service suggestions based on issue descriptions
  - Keyword matching system
  - Integration with booking workflow

### Version 1.4.0 (May 19, 2025)
- Security Enhancements:
  - Improved CSRF protection
  - Enhanced authentication workflow
  - Input validation improvements

### Planned Future Versions
- Location-based mechanic matching (maps integration)
- Mobile application development
- Payment gateway integration
- Subscription-based service plans
- Parts inventory and ordering system
- Fleet management services for businesses