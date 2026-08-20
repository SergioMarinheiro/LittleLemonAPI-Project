from django.shortcuts import render
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User, Group
from .helpers import manager_user, delivery_crew_user
from django.utils import timezone
from .permissions import IsManager
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    
    filterset_fields = ['category', 'featured']

   
    search_fields = ['title']

    
    ordering_fields = ['price', 'title']
    ordering = ['price']  # default ordering

    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method=='GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManager()]


class ManagerUsersView(APIView):
    
    permission_classes = [IsManager]

    def get(self, request):
        try:
            group = Group.objects.get(name='Manager')
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND)
        users = group.user_set.all().values('id', 'username', 'email')
        return Response(users, status=status.HTTP_200_OK)
    
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        group = Group.objects.get(name='Manager')
        group.user_set.add(user)
        return Response({"message": "User added to manager group"}, status=status.HTTP_201_CREATED)


class DelManagerUsersView(APIView):

    permission_classes = [IsManager]

    def delete(self,request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        group = Group.objects.get(name='Manager')
        group.user_set.remove(user)
        return Response({"message": "User added to manager group"}, status=status.HTTP_200_OK)


class DeliveryCrewUsersView(APIView):

    permission_classes = [IsManager]

    def get(self,request):
        try:
            group= Group.objects.get(name="Delivery Crew")              
        except Group.DoesNotExist:
            return Response({"error": "Group does not exist"}, status=status.HTTP_404_NOT_FOUND) 
        users = group.user_set.all().values('id', 'username', 'email')
        return Response(users, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        group = Group.objects.get(name='Delivery Crew')
        group.user_set.add(user)
        return Response({"message": "User added to manager group"}, status=status.HTTP_201_CREATED)

class DelDeliveryCrewUsersView(APIView):

    permission_classes = [IsManager]

    def delete(self,request, pk):
        try:
            user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error":"User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        group = Group.objects.get(name='Delivery Crew')
        group.user_set.remove(user)
        return Response({"message": "User removed from group"}, status=status.HTTP_200_OK)

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart_items = Cart.objects.filter(user=request.user)
        except Cart.DoesNotExist:
            return Response({"The cart is empty": []}, status=status.HTTP_200_OK)
        serializer = CartSerializer(cart_items)
        return Response(serializer.data)

    def post(self, request):
        menu_item_id = request.data.get('menuitem')
        quantity = int(request.data.get('quantity',1))    
        try:
            menu_item = MenuItem.objects.get(id=menu_item_id)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            menuitem=menu_item,
            defaults={
                'quantity': quantity,
                'unit_price': menu_item.price,
                'price': menu_item.price * quantity
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()

        serializer = CartSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message":"The cart was emptied"}, status=status.HTTP_200_OK)

class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]

    
    filterset_fields = ['status', 'delivery_crew']

   
    ordering_fields = ['date', 'total']
    ordering = ['-date']
    
    def get_queryset(self):
        user = self.request.user

        if manager_user(user):
            return Order.objects.all()
        elif delivery_crew_user(user):
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)        
    	
    def post(self,request):
                
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in cart_items)

        order = Order.objects.create(
            user= request.user,
            total= total,
            date= timezone.now().date()
        )            
          
        for item in cart_items:   
            OrderItem.objects.create(
                order= order,
                menuitem= item.menuitem,
                quantity= item.quantity,
                unit_price= item.unit_price,
                price= item.price
            )

        cart_items.delete()

        serializer = OrderSerializer(order) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class OrderIDView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,orderID):
        try:
            order = Order.objects.get(id= orderID)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if order.user != request.user:
            return Response({"message": "Incorrect order selected"}, status=status.HTTP_403_FORBIDDEN)
            

        order_items = OrderItem.objects.filter(order=order)
        order_serializer = OrderSerializer(order)
        items_serializer = OrderItemSerializer(order_items, many=True)

        data = {
            "order": order_serializer.data,
            "items": items_serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
    

    def delete(self, request, orderID):
        if not manager_user(request.user):
            return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        try:
            order = Order.objects.get(id=orderID)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({"message":"Order deleted"}, status=status.HTTP_200_OK)
    
    def patch(self, request, orderID):
        return self._update(request, orderID, partial=True)
    
    def put(self, request, orderID):
        return self._update(request, orderID, partial=False)
    

    def _update(self, request, orderID, partial):
        try:
            order = Order.objects.get(id= orderID)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        data = request.data

        
        if manager_user(user):
            if not partial:
                if "status" not in data or "delivery_crew" not in data:
                    return Response({"error": "Need status and delivery_crew info"},status=status.HTTP_400_BAD_REQUEST)
                 
            if "status" in data:
                order.status = bool(int(data["status"]))

            if "delivery_crew" in data:
                try:
                    crew = User.objects.get(id=data["delivery_crew"])
                    if not delivery_crew_user(crew):
                        return Response({"error": "User is not delivery crew"}, status=status.HTTP_404_NOT_FOUND)
                    order.delivery_crew = crew
                except User.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
                
            order.save()
            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
                
        elif delivery_crew_user(user):
            if order.delivery_crew != user:
                return Response({"error": "Not assigned to this order"}, status=status.HTTP_403_FORBIDDEN)
            
            if "status" not in data:
                return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)

            order.status = bool(int(data["status"]))
            order.save()

            return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


    