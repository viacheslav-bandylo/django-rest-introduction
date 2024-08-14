from django.urls import path
from .views import *

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list-create'),  # Для получения всех книг и создания новой книги
    path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),  # Для операций с одной книгой
    path('genres/', create_genre, name='create-genre'),  # Маршрут для создания жанров
]
