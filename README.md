# GhorerBazar - Online Grocery Shop Project

GhorerBazar is an online grocery shopping platform built using Django and Django REST Framework (DRF). This project allows users to browse, purchase, and manage grocery items efficiently. Admins and Sellers have dedicated roles with specific permissions to manage products, inventory, and orders.

---

## Table of Contents

1. [Features](#features)  
2. [Models](#models)  
3. [API Endpoints](#api-endpoints)  
4. [Authentication & Roles](#authentication--roles)  
5. [Setup and Installation](#setup-and-installation)  
6. [Running the Project](#running-the-project)  
7. [Future Improvements](#future-improvements)

---

## Features

### User Features
- User registration and authentication (with JWT and Djoser)
- Email verification and password reset
- Browsing products and filtering by category, name, or price
- Adding products to shopping cart
- Creating orders and viewing purchase history
- Wishlist functionality for future purchases

### Seller Features
- Sellers can add their own products
- View sales history (orders containing their products)
- Manage product inventory
- Read-only view of orders containing their products

### Admin Features
- Full access to all products and orders
- Manage users and their roles
- Edit, delete, or approve products added by sellers

---

## Models

### Users (`users.models.User`)
- `email` (unique, login field)
- `first_name`, `last_name`, `address`, `phone_number`
- `balance` (DecimalField, default=0)
- `role` (`user`, `admin`, `seller`) – role determines permissions

### Product (`product.models.Product`)
- `name`, `description`, `price`, `stock`
- `category` (FK to Category)
- `seller` (FK to User, optional)
- `images` (CloudinaryField for multiple product images)

### Category (`product.models.Category`)
- `name`, `description`
- Annotated with `product_count` in queries

### Review (`product.models.Review`)
- `user` (FK to User)
- `product` (FK to Product)
- `ratings` (1-5)
- `comment`, `created_at`, `updated_at`

### Cart & CartItem (`order.models.Cart`, `order.models.CartItem`)
- Each user has a one-to-one `Cart`
- `CartItem` links a product with quantity

### Order & OrderItem (`order.models.Order`, `order.models.OrderItem`)
- `Order` contains user, status, total price, created_at, updated_at
- `OrderItem` links order to a product with quantity, price, and total_price

---

## API Endpoints

### Authentication
- `/api/v1/auth/users/` – Register new users
- `/api/v1/auth/jwt/create/` – Obtain JWT token
- `/api/v1/auth/users/me/` – Retrieve current user profile
- `/api/v1/auth/users/reset_password/` – Reset password

### Products
- `/api/v1/products/` – List, create (admin/seller), update, delete (admin/seller)
- `/api/v1/products/{id}/` – Retrieve specific product
- `/api/v1/products/{product_id}/reviews/` – List, create, update, delete reviews
- `/api/v1/products/{product_id}/images/` – Upload images (admin/seller)

### Categories
- `/api/v1/categories/` – List categories
- `/api/v1/categories/{id}/` – Retrieve specific category

### Cart
- `/api/v1/carts/` – Create or retrieve user cart
- `/api/v1/carts/{cart_id}/items/` – Add, update, delete cart items

### Orders
- `/api/v1/orders/` – List all orders (admin) or user orders
- `/api/v1/orders/` (POST) – Create order from cart
- `/api/v1/orders/{id}/cancel/` – Cancel order (user or admin)
- `/api/v1/orders/{id}/update_status/` – Update order status (admin)

### Seller Dashboard
- `/api/v1/seller-products/` – List products added by logged-in seller
- `/api/v1/seller-orders/` – List orders containing seller's products

---

## Authentication & Roles

| Role   | Permissions                                                                 |
|--------|----------------------------------------------------------------------------|
| User   | Browse products, manage cart, create orders, add reviews, wishlist         |
| Seller | Add products, manage inventory, view own sales orders                      |
| Admin  | Full access to all models, manage users, approve/edit/delete any product   |

**JWT Authentication** is used for all protected endpoints. Include `Authorization: JWT <token>` in request headers.

---

## Setup and Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd GhorerBazar
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file with the following variables:

```bash
SECRET_KEY=<your-secret-key>
DATABASE_URL=<your-database-url>
cloud_name=<cloudinary-cloud-name>
cloudinary_api_key=<cloudinary-api-key>
api_secret=<cloudinary-api-secret>
```

5. Apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create a superuser (admin):

```bash
python manage.py createsuperuser
```

7. Run the development server:

```bash
python manage.py runserver
```

8. Access the Swagger API documentation:

```bash
http://127.0.0.1:8000/swagger/
```


## Running the Project

### Admin panel: /admin/

### API root: /api/v1/

### Swagger docs: /swagger/

### Redoc docs: /redoc/

## License
This project is licensed under the BSD License.