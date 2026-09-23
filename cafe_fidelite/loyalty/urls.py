from django.urls import path

from . import views


app_name = "loyalty"

urlpatterns = [
    path("", views.client_recherche_creation, name="client_recherche_creation"),
    path(
        "<int:client_id>/achat/",
        views.enregistrer_achat,
        name="enregistrer_achat",
    ),
]