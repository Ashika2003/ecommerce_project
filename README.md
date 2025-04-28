This is a Django REST API for a small e-commerce system with JWT authentication, caching, and real-time notifications.
Features

User Authentication (JWT)

Registration and Login
User Profile Management
Order History


Product Management

CRUD operations for Products and Categories
Stock Management


Order System

Cart Management
Order Placement
Order Status Updates


Caching & Optimization

Redis Caching
Query Optimization


Pagination & Filtering

Product Pagination
Filter by Category/Price/Stock


Real-time Notifications

WebSocket Order Status Updates



Tech Stack

Django & Django REST Framework: Backend framework
PostgreSQL: Database
Redis: Caching layer
Django Channels: WebSocket support for real-time notifications
SimpleJWT: JWT Authentication

Project Setup
Prerequisites

Python 3.8+
PostgreSQL
Redis

Installation Steps

Clone the repository

Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Set up PostgreSQL
Create a new PostgreSQL database:
psql -U postgres
CREATE DATABASE ecommerce_db;
\q

Configure Environment Variables
Create a .env file in the project root with the following variables:
DEBUG=True
SECRET_KEY=your_secret_key
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1

Run Migrations
python manage.py makemigrations
python manage.py migrate

Create Superuser
python manage.py createsuperuser

Run Development Server
python manage.py runserver

Run WebSocket Server (Separate Terminal)
python manage.py runserver


API Endpoints
Authentication

POST /api/users/register/: Register a new user
POST /api/users/login/: Log in and get JWT tokens
POST /api/users/token/refresh/: Refresh JWT token
GET/PUT /api/users/profile/: Get or update user profile
PUT /api/users/change-password/: Change user password

Products

GET /api/products/categories/: List all categories
GET /api/products/categories/{slug}/: Get category details
GET /api/products/: List all products (paginated, filterable)
GET /api/products/{slug}/: Get product details

Cart & Orders

GET /api/orders/cart/: View current cart
POST /api/orders/cart-items/: Add item to cart
PUT/DELETE /api/orders/cart-items/{id}/: Update/remove cart item
DELETE /api/orders/cart/clear/: Clear cart
POST /api/orders/orders/: Place a new order
GET /api/orders/orders/: List user orders
GET /api/orders/orders/{id}/: Get order details
PATCH /api/orders/orders/{id}/update_status/: Update order status (admin only)
