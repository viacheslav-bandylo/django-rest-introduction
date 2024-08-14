from django.urls import path
from .views import *

urlpatterns = [
    path('books/', book_list, name='book-list'),  # Маршрут для получения всех книг
    path('books/<int:pk>/', book_detail, name='book-detail'),
    path('books/create/', book_create, name='book-create'),
    path('books/<int:pk>/update/', book_update, name='book-update'),
    path('books/<int:pk>/delete/', book_delete, name='book-delete'),
]
