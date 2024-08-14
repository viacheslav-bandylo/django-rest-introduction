from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import *
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


class BookListView(APIView, PageNumberPagination):
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



class BookListCreateView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailUpdateDeleteView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
        serializer = BookCreateSerializer(data=request.data)
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
