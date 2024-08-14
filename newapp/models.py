from django.db import models


# Определение модели
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=50)
    published_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_bestseller = models.BooleanField(default=False, null=True, blank=True)
