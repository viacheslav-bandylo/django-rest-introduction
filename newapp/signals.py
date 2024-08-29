import logging

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Book, Genre
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.mail import send_mail


@receiver(post_save, sender=Book)
def notify_admin_on_new_order(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'New Book Created',
            f'Book {instance.id} has been created.',
            'admin@gmail.com',
            ['admin@gmail.com'],
        )


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Book)
def book_saved(sender, instance, created, **kwargs):
    if created:
        print(f'New book created: {instance.title}')
    else:
        print(f'Book updated: {instance.title}')

# # Подключение функции-обработчика к сигналу
# post_save.connect(book_saved, sender=Book)


def update_timestamp(sender, instance, **kwargs):
    instance.updated_at = timezone.now()


# Подключение функции-обработчика к сигналу
pre_save.connect(update_timestamp, sender=Book)

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Book)
def log_book_deletion(sender, instance, **kwargs):
    logger.info(f'Book deleted: {instance.name}')
