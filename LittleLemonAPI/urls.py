from django.urls import path
from . import views

urlpatterns = [
    path("menu-items/", views.MenuItemView.as_view()),
    path("menu-items/<int:pk>/", views.SingleMenuItemView.as_view()),
    path('groups/manager/users/', views.ManagerUsersView.as_view()),
    path('groups/manager/users/<int:pk>/', views.DelManagerUsersView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewUsersView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DelDeliveryCrewUsersView.as_view()),
    path('cart/menu-items/', views.CartView.as_view()),
    path('orders/', views.OrderView.as_view()),
    path('orders/<int:orderID>', views.OrderIDView.as_view()),
]