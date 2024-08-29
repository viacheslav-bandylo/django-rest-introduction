from django.db import models
from rest_framework.authtoken.admin import User

from newapp.managers import SoftDeleteManager


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = [
            ("can_get_statistic", "Can get genres statistic"),
        ]


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    established_date = models.DateField()


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    published_date = models.DateField()
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_bestseller = models.BooleanField(default=False)
    genres = models.ManyToManyField(Genre, related_name='books')
    is_banned = models.BooleanField(default=False)  # Поле, указывающее на запрещенную книгу
    is_deleted = models.BooleanField(default=False)  # Поле для мягкого удаления
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()
