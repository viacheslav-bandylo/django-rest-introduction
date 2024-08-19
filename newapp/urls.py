from django.urls import path
from .views import *

urlpatterns = [
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),
    path('books/expensive/', ExpensiveBooksView.as_view(), name='book-expensive'),
    # path('books/', BookListView.as_view(), name='book-list-create'),  # Для получения всех книг и создания новой книги
    # path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),  # Для операций с одной книгой
    path('genres/', GenreListCreateView.as_view(), name='create-genre'),  # Маршрут для создания жанров
    path('genres/<str:genre_name>/', GenreDetailUpdateDeleteView.as_view(), name='genre-detail-update-delete'),
]
