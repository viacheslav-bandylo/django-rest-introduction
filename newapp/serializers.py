from django.utils import timezone
from rest_framework import serializers
from .models import Book, Publisher  # Импортируйте вашу модель
from .validators import validate_title_length

from .models import Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class BookDetailSerializer(serializers.ModelSerializer):
    publisher = PublisherSerializer()  # Вложенный сериализатор

    class Meta:
        model = Book
        fields = '__all__'


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author']


class BookSerializer(serializers.ModelSerializer):
    publisher = serializers.PrimaryKeyRelatedField(queryset=Publisher.objects.all())
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)

    class Meta:
        model = Book
        fields = '__all__'


    # def validate_price(self, value):
    #     if value < 1:
    #         raise serializers.ValidationError("Price must be at least 1.")
    #     return value
    #
    # def validate(self, data):
    #     if data['discounted_price'] and data['discounted_price'] > data['price']:
    #         raise serializers.ValidationError("Discounted price cannot be higher than the original price.")
    #     return data

    # def create(self, validated_data):
    #     publisher_name = validated_data.pop('publisher_name')
    #     established_date = timezone.now()
    #     publisher, create = Publisher.objects.get_or_create(name=publisher_name, established_date=established_date)
    #     book = Book.objects.create(publisher=publisher, **validated_data)
    #     return book
    #
    # def update(self, instance, validated_data):
    #     # Предобработка текстового поля title как заголовок
    #     if 'title' in validated_data:
    #         validated_data['title'] = validated_data['title'].strip().title()
    #
    #     return super().update(instance, validated_data)




