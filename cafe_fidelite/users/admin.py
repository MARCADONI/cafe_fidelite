from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User


if settings.DJANGO_ADMIN_FORCE_ALLAUTH:

    admin.autodiscover()

    admin.site.login = secure_admin_login(
        admin.site.login
    )


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserAdminChangeForm

    add_form = UserAdminCreationForm

    fieldsets = (
        (
            None,
            {"fields": ("username", "password")},
        ),
        (
            _("Personal info"),
            {"fields": ("name", "email")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
            },
        ),
    )

    list_display = [
        "username",
        "name",
        "is_superuser",
    ]

    search_fields = ["name"]

    # =============================================
    # SECURISATION DE L'ADMINISTRATION UTILISATEURS
    # =============================================

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser