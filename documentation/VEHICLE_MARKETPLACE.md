# Vehicle Marketplace - Technical Documentation

## Overview

The Vehicle Marketplace is a key feature of the Harare Mobile Mechanics platform, allowing users to list their vehicles for sale and browse available vehicles. This document provides technical details on the implementation of this feature.

## Table of Contents

1. [Data Model](#data-model)
2. [Core Functions](#core-functions)
3. [Routes and Views](#routes-and-views)
4. [Form Definitions](#form-definitions)
5. [Templates](#templates)
6. [User Interface](#user-interface)
7. [Integration with Other Services](#integration-with-other-services)

## Data Model

The Vehicle Marketplace uses the `Vehicle4Sale` data model to represent vehicles listed for sale:

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

## Core Functions

The following core functions in `data.py` handle vehicle marketplace operations:

### Getting Vehicles

```python
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
```

### Getting a Specific Vehicle

```python
def get_vehicle_for_sale_by_id(vehicle_id):
    """Get a vehicle listing by ID"""
```

### Getting User Listings

```python
def get_user_vehicle_listings(user_id):
    """Get all vehicle listings for a specific user"""
```

### Creating a Vehicle Listing

```python
def create_vehicle_listing(seller_id, make, model, year, price, condition, mileage, color, 
                           transmission, fuel_type, description, features=None, images=None):
    """Create a new vehicle listing"""
```

### Updating a Vehicle Listing

```python
def update_vehicle_listing(vehicle_id, **kwargs):
    """Update an existing vehicle listing"""
```

### Marking a Vehicle as Sold

```python
def mark_vehicle_as_sold(vehicle_id, buyer_id=None):
    """Mark a vehicle as sold"""
```

### Deleting a Vehicle Listing

```python
def delete_vehicle_listing(vehicle_id):
    """Delete a vehicle listing"""
```

## Routes and Views

The following routes in `routes.py` handle vehicle marketplace interactions:

### Main Marketplace Page

```python
@app.route('/marketplace')
def vehicle_marketplace():
    """Main marketplace page for vehicle listings"""
```

This route displays all vehicle listings with optional filtering, supporting search parameters for make, model, year range, price range, and condition.

### Vehicle Detail Page

```python
@app.route('/marketplace/vehicle/<int:vehicle_id>')
def vehicle_listing_detail(vehicle_id):
    """Show detailed page for a specific vehicle listing"""
```

This route displays detailed information for a specific vehicle listing, including seller contact details.

### User's Vehicle Listings

```python
@app.route('/marketplace/my-listings')
def my_vehicle_listings():
    """View all user's vehicle listings"""
```

This route shows all vehicle listings created by the logged-in user, with options to edit, mark as sold, or delete.

### Create Vehicle Listing

```python
@app.route('/marketplace/create', methods=['GET', 'POST'])
def create_vehicle_listing():
    """Create a new vehicle listing"""
```

This route handles both the form display and submission for creating a new vehicle listing.

### Edit Vehicle Listing

```python
@app.route('/marketplace/edit/<int:vehicle_id>', methods=['GET', 'POST'])
def edit_vehicle_listing(vehicle_id):
    """Edit an existing vehicle listing"""
```

This route allows users to edit their existing vehicle listings.

### Delete Vehicle Listing

```python
@app.route('/marketplace/delete/<int:vehicle_id>', methods=['POST'])
def delete_vehicle_listing_route():
    """Delete a vehicle listing"""
```

This route handles the deletion of a vehicle listing.

### Mark Vehicle as Sold

```python
@app.route('/marketplace/mark-sold/<int:vehicle_id>', methods=['POST'])
def mark_vehicle_sold():
    """Mark a vehicle as sold"""
```

This route allows sellers to mark a vehicle as sold, optionally specifying a buyer.

## Form Definitions

The marketplace uses two main forms defined in `forms.py`:

### Vehicle Listing Form

```python
class VehicleListingForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=2100)])
    price = FloatField('Price (USD)', validators=[DataRequired(), NumberRange(min=0)])
    condition = SelectField('Condition', choices=[
        ('New', 'New'), 
        ('Used', 'Used'), 
        ('Certified Pre-Owned', 'Certified Pre-Owned')
    ], validators=[DataRequired()])
    mileage = IntegerField('Mileage', validators=[DataRequired(), NumberRange(min=0)])
    color = StringField('Color', validators=[DataRequired(), Length(max=30)])
    transmission = SelectField('Transmission', choices=[
        ('Automatic', 'Automatic'), 
        ('Manual', 'Manual'), 
        ('Semi-Automatic', 'Semi-Automatic')
    ], validators=[DataRequired()])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'), 
        ('Diesel', 'Diesel'), 
        ('Electric', 'Electric'), 
        ('Hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=20, max=1000)])
    features = StringField('Features (comma separated)', validators=[Optional()])
    images = MultipleFileField('Vehicle Images', validators=[Optional()])
    submit = SubmitField('List Vehicle')
```

### Vehicle Search Form

```python
class VehicleSearchForm(FlaskForm):
    make = StringField('Make', validators=[Optional()])
    model = StringField('Model', validators=[Optional()])
    min_year = IntegerField('Min Year', validators=[Optional(), NumberRange(min=1900, max=2100)])
    max_year = IntegerField('Max Year', validators=[Optional(), NumberRange(min=1900, max=2100)])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    condition = SelectField('Condition', choices=[
        ('', 'Any'), 
        ('New', 'New'), 
        ('Used', 'Used'), 
        ('Certified Pre-Owned', 'Certified Pre-Owned')
    ], validators=[Optional()])
    submit = SubmitField('Search')
```

## Templates

The marketplace feature includes the following templates:

### marketplace.html
Main page for browsing and searching vehicle listings.

- Displays search filters at the top
- Shows all available vehicles in a card-based grid layout
- Includes pagination for large numbers of listings
- Provides a "List Your Vehicle" button for logged-in users

### vehicle_detail.html
Detailed view of a specific vehicle listing.

- Image carousel for vehicle photos
- Detailed vehicle specifications
- Seller contact information
- Related services (e.g., pre-purchase inspection)
- Edit and delete options for the owner

### my_listings.html
Management page for a user's vehicle listings.

- Table view of all user listings
- Status indicators (active, sold)
- Action buttons for edit, mark as sold, and delete
- Modal confirmations for delete and mark as sold actions

### create_listing.html and edit_listing.html
Forms for creating and editing vehicle listings.

- Structured sections for different types of information
- Image upload functionality
- Validation feedback for form fields

## User Interface

The marketplace UI follows these design principles:

1. **Clean Card-Based Layout**: Vehicle listings are displayed in cards with key information visible at a glance.
2. **Prominent Search and Filtering**: Search filters are displayed prominently at the top of the marketplace.
3. **Visual Hierarchy**: Important information like price and vehicle name is emphasized.
4. **Clear Call-to-Actions**: Buttons for key actions are clearly visible.
5. **Responsive Design**: The layout adapts to different screen sizes for mobile and desktop viewing.

### Key UI Components:

1. **Search Panel**: Collapsible search panel with form controls for all filter criteria.
2. **Vehicle Cards**: Standardized cards showing image, make/model, year, price, and key specs.
3. **Detail Page Header**: Vehicle title, price, and key specs are presented prominently at the top.
4. **Contact Section**: Seller contact information is clearly accessible.
5. **Management Controls**: For owners, edit and delete controls are available.

## Integration with Other Services

The Vehicle Marketplace integrates with other platform features:

1. **User Authentication**: Only logged-in users can create listings or contact sellers.
2. **Mechanic Services**: Links to pre-purchase inspection services for potential buyers.
3. **Notification System**: Notifications are sent for listing creation, updates, and when vehicles are marked as sold.
4. **User Profiles**: Seller information is pulled from user profiles.

## Future Enhancements

Planned enhancements for the Vehicle Marketplace feature:

1. **Advanced Search Options**: More detailed search parameters including transmission type, fuel type, etc.
2. **Image Gallery Improvements**: Support for multiple images with better organization and viewing options.
3. **Saved Searches**: Allow users to save searches and receive notifications for new listings.
4. **Similar Listings**: Display similar vehicles on the detail page.
5. **Market Value Estimation**: Provide estimated market value based on similar vehicles.
6. **Integration with Maps**: Show the location of vehicles on a map.
7. **Vehicle History Reports**: Integration with vehicle history report services.
8. **Direct Messaging**: In-platform messaging between buyers and sellers.