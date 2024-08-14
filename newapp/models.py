from django.db import models


class Publisher(models.Model):
    name = models.CharField(max_length=100)
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
