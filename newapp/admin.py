from django.contrib import admin
from newapp.models import Book, Publisher


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')

admin.site.register(Publisher)
