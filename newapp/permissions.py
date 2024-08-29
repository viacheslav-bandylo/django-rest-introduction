from datetime import datetime

from rest_framework.permissions import BasePermission


class CanGetStatisticPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm('newapp.can_get_statistic')


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает редактирование объектов только их владельцам, остальным - только чтение.
    """
    def has_object_permission(self, request, view, obj):
        # Все пользователи могут просматривать
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Только владелец может изменять объект
        return obj.owner == request.user


class IsAdminOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Все пользователи могут просматривать
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # Только администратор или владелец может изменять объект
        return request.user.is_staff or obj.owner == request.user


class IsWorkHour(BasePermission):
    def has_object_permission(self, request, view, obj):
        current_hour = datetime.now().hour
        # Допустим, рабочие часы с 9 до 18
        return 9 <= current_hour < 18
