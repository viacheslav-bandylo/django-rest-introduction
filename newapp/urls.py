from django.urls import path, include, re_path
from .views import *
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import GenreListRetrieveUpdateViewSet


router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'books', BookViewSet)
# router.register(r'genres', GenreListRetrieveUpdateViewSet)
# router.register(r'genres', GenreReadOnlyViewSet)
# router2 = SimpleRouter()
# router2.register(r'books', BookViewSet)


urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^books/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', books_by_date_view, name='books-by-date'),
    # path('', include(router2.urls)),
    # path('books/', BookListCreateView.as_view(), name='book-list-create'),
    # path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),
    # path('books/expensive/', ExpensiveBooksView.as_view(), name='book-expensive'),
    # path('books/', BookListView.as_view(), name='book-list-create'),  # Для получения всех книг и создания новой книги
    # path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),  # Для операций с одной книгой
    # path('genres/', GenreListCreateView.as_view(), name='create-genre'),  # Маршрут для создания жанров
    # path('genres/<str:genre_name>/', GenreDetailUpdateDeleteView.as_view(), name='genre-detail-update-delete'),
]
