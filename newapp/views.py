from datetime import datetime

from django.contrib.auth import authenticate
from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import *
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response
from rest_framework import status, filters
from .models import Book
from .serializers import BookSerializer
from rest_framework import mixins, viewsets
from .models import Genre
from .serializers import GenreSerializer
from rest_framework.authentication import BasicAuthentication, TokenAuthentication


class ReadOnlyOrAuthenticatedView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response({"message": "This is readable by anyone, but modifiable only by authenticated users."})

    def post(self, request):
        return Response({"message": "Data created by authenticated user!"})


class PublicView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "This is accessible by anyone!"})


def set_jwt_cookies(response, user):
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token

    # Устанавливает JWT токены в куки.
    access_expiry = datetime.utcfromtimestamp(access_token['exp'])
    refresh_expiry = datetime.utcfromtimestamp(refresh_token['exp'])

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=access_expiry
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=refresh_expiry
    )


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = Response({
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
            set_jwt_cookies(response, user)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Используем exp для установки времени истечения куки
            access_expiry = datetime.utcfromtimestamp(access_token['exp'])
            refresh_expiry = datetime.utcfromtimestamp(refresh['exp'])

            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=False,  # Используйте True для HTTPS
                samesite='Lax',
                expires=access_expiry
            )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax',
                expires=refresh_expiry
            )
            return response
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class ProtectedDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Hello, authenticated user!", "user": request.user.username})


@api_view(['GET'])
def books_by_date_view(request, year, month, day):
    books = Book.objects.filter(published_date__year=year, published_date__month=month, published_date__day=day)
    serializer = BookSerializer(books, many=True)
    return Response({'date': f"{year}-{month}-{day}", 'books': serializer.data})


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    @action(detail=False, methods=['get'])
    def statistic(self, request):
        genres_with_book_counts = Genre.objects.annotate(book_count=Count('books'))
        data = [
            {
                "id": genre.id,
                "genre": genre.name,
                "book_count": genre.book_count
            }
            for genre in genres_with_book_counts
        ]
        return Response(data)


class GenreListRetrieveUpdateViewSet(mixins.UpdateModelMixin, mixins.RetrieveModelMixin,
                                     mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookCursorPagination(CursorPagination):
    page_size = 3
    ordering = 'price'  # Поле для курсора


# class BookPagination(PageNumberPagination):
#     page_size = 3  # Количество элементов на странице
#     page_size_query_param = 'page_size'
#     max_page_size = 100


class BookListCreateView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # pagination_class = BookPagination
    # pagination_class = LimitOffsetPagination
    # pagination_class = BookCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author', 'publisher', 'is_bestseller']  # Поля для фильтрации
    search_fields = ['title', 'author']  # Поля для поиска
    ordering_fields = ['published_date', 'price']  # Поля для сортировки

    # Добавление кастомной логики перед сохранением
    def create(self, request, *args, **kwargs):
        # Получение данных из запроса
        data = request.data.copy()
        # Кастомная логика: Установка значения по умолчанию для автора, если не указан
        if 'author' not in data or not data['author']:
            data['author'] = 'Unknown Author'
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['include_related'] = self.request.query_params.get('include_related', 'false').lower() == 'true'
        return context


class ExpensiveBooksView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def list(self, request, *args, **kwargs):
        # Вычисление средней цены
        average_price = Book.objects.aggregate(average_price=Avg('price'))['average_price']
        # Получение книг с ценой выше средней
        queryset = Book.objects.filter(price__gt=average_price)
        # Сериализация данных
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Представление для получения, обновления и удаления конкретного объекта
class BookDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    # Переопределение метода для добавления кастомной логики
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        # Добавление поля к ответу, проверяющего, что цена со скидкой меньше цены
        if response.data.get('discounted_price') is not None and response.data.get('price') is not None:
            response.data['is_discounted'] = response.data['discounted_price'] < response.data['price']
        else:
            response.data['is_discounted'] = False

        return response

    # Добавление кастомной проверки перед обновлением
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Пример проверки: цена книги не должна быть ниже минимальной
        if serializer.validated_data.get('price', instance.price) < 5.00:
            return Response({'error': 'Price cannot be less than 5.00'}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data)

    # Добавление кастомной логики при удалении объекта
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        # Пример кастомной логики: логирование успешного удаления
        print(f"Book deleted: {instance}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        # Получение параметра pk из URL
        pk = self.kwargs.get('pk')

        # Попытка найти объект по pk, исключая запрещенные
        try:
            book = self.queryset.get(pk=pk, is_banned=False)
        except Book.DoesNotExist:
            # Обработка ошибки, если объект не найден или запрещен
            raise NotFound(detail=f"Book with id '{pk}' not found or is banned.")

        return book


class GenreListCreateView(ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class GenreDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'name'  # Указывает использовать поле 'name' для поиска
    lookup_url_kwarg = 'genre_name'  # Указывает параметр URL 'genre_name' для получения значения



# class BookListCreateView(GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookListSerializer
#
#     def get(self, request, *args, **kwargs):
#         books = self.get_queryset()
#         serializer = self.get_serializer(books, many=True)
#         return Response(serializer.data)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#
# class BookDetailUpdateDeleteView(GenericAPIView):
#     queryset = Book.objects.all()
#     serializer_class = BookDetailSerializer
#
#     def get(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book)
#         return Response(serializer.data)
#
#     def put(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def patch(self, request, *args, **kwargs):
#         book = self.get_object()
#         serializer = self.get_serializer(book, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#
#     def delete(self, request, *args, **kwargs):
#         book = self.get_object()
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


class BookListView(APIView):
    page_size = 2  # Значение по умолчанию

    def get(self, request):
        books = Book.objects.all()
        page_size = self.get_page_size(request)  # Получение параметра page_size из запроса
        self.page_size = page_size  # Установка значения page_size
        results = self.paginate_queryset(books, request, view=self)
        serializer = BookDetailSerializer(results, many=True)
        return self.get_paginated_response(serializer.data)

    def get_page_size(self, request):
        """
        Переопределение метода get_page_size для поддержки параметра page_size.
        """
        page_size = request.query_params.get('page_size')
        if page_size and page_size.isdigit():
            return int(page_size)
        return self.page_size  # Использование значения по умолчанию


# https://127.0.0.1:8000/books/?author=John&published_year=2023

# class BookListView(APIView):
#     def get(self, request):
#         filters = {}
#         author = request.query_params.get('author')
#         published_year = request.query_params.get('published_year')
#
#         if author:
#             filters['author'] = author
#
#         if published_year:
#             filters['published_date__year'] = published_year
#
#         books = Book.objects.filter(**filters)
#         serializer = BookDetailSerializer(books, many=True)  # Заменим на BookDetailSerializer чтобы видеть много полей
#         return Response(serializer.data)



# class BookListCreateView(APIView):
#     def get(self, request):
#         books = Book.objects.all()
#         serializer = BookSerializer(books, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         serializer = BookSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BookDetailUpdateDeleteView(APIView):
#     def get(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = BookSerializer(book)
#         return Response(serializer.data)
#
#     def put(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         serializer = BookSerializer(book, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         try:
#             book = Book.objects.get(pk=pk)
#         except Book.DoesNotExist:
#             return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#         book.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def create_genre(request):
    serializer = GenreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response


@api_view(['GET', 'POST'])
def book_list_create(request):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def book_detail_update_delete(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookDetailSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BookCreateSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        book.delete()
        return Response({'message': 'Book deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET'])
# def book_list(request):
#     books = Book.objects.all()
#     serializer = BookListSerializer(books, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# @api_view(['GET'])
# def book_detail(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     serializer = BookDetailedSerializer(book)
#     return Response(serializer.data, status=status.HTTP_200_OK)


# @api_view(['GET', 'POST'])
# def book_list_create(request):
#     if request.method == 'GET':
#         books = Book.objects.all()
#         serializer = BookListSerializer(books, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     elif request.method == 'POST':
#         serializer = BookCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# def book_update(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     serializer = BookCreateSerializer(book, data=request.data)
#
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     else:
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['DELETE'])
# def book_delete(request, pk):
#     try:
#         book = Book.objects.get(pk=pk)
#     except Book.DoesNotExist:
#         return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
#
#     book.delete()
#     return Response({'message': 'Book deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
