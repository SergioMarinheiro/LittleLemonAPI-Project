# LittleLemonAPI-Project

A full-featured REST API for a restaurant management system, built with **Django REST Framework**.
Serves three distinct user roles - customers, managers and delivery crew - through role-based
access control.

## What it does

Handles the full ordering workflow: browsing the menu, managing a cart, placing an order, and
assigning it to delivery crew - with each role restricted to the operations it is allowed to perform.

## Tech stack

Python | Django | Django REST Framework | Djoser | SQLite | Pipenv | Token Authentication

## Roles and permissions

| Role | Can do |
| ---- | ------ |
| Customer | Browse menu, manage own cart, place orders, view own orders |
| Manager | Manage menu items, assign orders to delivery crew, view all orders |
| Delivery crew | View assigned orders, mark orders as delivered |

## Endpoints

| Method | Route | Role | Description |
| ------ | ----- | ---- | ----------- |
| GET | `/api/menu-items` | All | List menu items (filter, search, sort, paginate) |
| POST | `/api/menu-items` | Manager | Create a menu item |
| GET/PUT/DELETE | `/api/menu-items/{id}` | Manager | Manage a single menu item |
| GET/POST/DELETE | `/api/cart/menu-items` | Customer | Manage the current cart |
| GET/POST | `/api/orders` | Customer | List own orders / place an order from the cart |
| GET/PUT/PATCH | `/api/orders/{id}` | Role-dependent | View or update an order |
| GET/POST/DELETE | `/api/groups/manager/users` | Manager | Manage the manager group |
| GET/POST/DELETE | `/api/groups/delivery-crew/users` | Manager | Manage the delivery crew group |
| POST | `/auth/token/login` | All | Obtain an authentication token |

## Features

- **Token authentication** via Djoser
- **Role-based permissions** enforced per endpoint
- **Filtering, searching, sorting and pagination** on menu and order endpoints
- **Throttling** for both authenticated and anonymous users
- **Correct HTTP status codes** for success, validation failure, unauthorised access and missing
  resources

## Running locally

```bash
git clone https://github.com/SergioMarinheiro/LittleLemonAPI-Project.git
cd LittleLemonAPI-Project
pipenv install
pipenv shell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then obtain a token at `/auth/token/login` and pass it as `Authorization: Token <token>`.

The project uses SQLite by default, so no database server is needed to run it locally.

## Notes

Built as the capstone project for the Meta Back-End Developer Professional Certificate.
