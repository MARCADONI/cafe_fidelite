from django.contrib import admin

from .models import Achat, CartePrepayee, Client, Fidelite


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("nom", "telephone", "courriel", "date_creation")
    search_fields = ("nom", "telephone", "courriel")

@admin.register(Fidelite)
class FideliteAdmin(admin.ModelAdmin):
    list_display = ("client", "progression", "recompenses")
    search_fields = ("client__nom", "client__telephone")


@admin.register(CartePrepayee)
class CartePrepayeeAdmin(admin.ModelAdmin):
    list_display = ("client", "cafes_restants", "date_emission", "active")
    search_fields = ("client__nom", "client__telephone")
    list_filter = ("active",)


@admin.register(Achat)
class AchatAdmin(admin.ModelAdmin):
    list_display = ("client", "type_achat", "carte_prepayee", "date_achat")
    search_fields = ("client__nom", "client__telephone")
    list_filter = ("type_achat",)