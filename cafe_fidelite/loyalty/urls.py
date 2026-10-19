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

    path(
    "rapports/",
    views.rapport_statistiques,
    name="rapport_statistiques",
),

    path(
    "fusion/",
    views.fusion_clients,
    name="fusion_clients",
),
    path(
    "anonymisation/",
    views.anonymisation_client,
    name="anonymisation_client",
),

    path(
    "audit/",
    views.journal_audit,
    name="journal_audit",
),
]