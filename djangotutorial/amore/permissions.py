from rest_framework import permissions


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Cualquiera puede leer (GET, HEAD, OPTIONS).
    Solo un usuario autenticado y con is_staff=True puede escribir
    (POST, PUT, PATCH, DELETE) — igual que la restricción que ya existe
    en el sitio web para el catálogo de productos (StaffRequiredMixin).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
