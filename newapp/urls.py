from django.urls import path, include, re_path
from rest_framework.authtoken.views import obtain_auth_token

from .views import *
from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import GenreListRetrieveUpdateViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'genres', GenreViewSet)
router.register(r'books', BookViewSet)
# router.register(r'genres', GenreListRetrieveUpdateViewSet)
# router.register(r'genres', GenreReadOnlyViewSet)
# router2 = SimpleRouter()
# router2.register(r'books', BookViewSet)


urlpatterns = [
    path('api/', ReadOnlyOrAuthenticatedView.as_view(), name='home'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('protected/', ProtectedDataView.as_view(), name='protected-data'),
    path('books/<int:pk>/', BookDetailUpdateDeleteView.as_view(), name='book-detail-update-delete'),
    path('', include(router.urls)),
    re_path(r'^books/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', books_by_date_view, name='books-by-date'),
    path('user-book/', UserBookListView.as_view(), name='user-book'),
    # path('', include(router2.urls)),
    # path('books/', BookListCreateView.as_view(), name='book-list-create'),
    # path('books/expensive/', ExpensiveBooksView.as_view(), name='book-expensive'),
    # path('books/', BookListView.as_view(), name='book-list-create'),  # Для получения всех книг и создания новой книги
    # path('genres/', GenreListCreateView.as_view(), name='create-genre'),  # Маршрут для создания жанров
    # path('genres/<str:genre_name>/', GenreDetailUpdateDeleteView.as_view(), name='genre-detail-update-delete'),
]
