from django.conf import settings
from django.db import migrations


def migrer_donnees_v2(apps, schema_editor):
    """
    Rattache les donnees historiques de la V2
    a la premiere succursale.
    """

    Succursale = apps.get_model("loyalty", "Succursale")

    AffectationSuccursale = apps.get_model(
        "loyalty",
        "AffectationSuccursale"
    )

    Achat = apps.get_model("loyalty", "Achat")

    EmissionCarte = apps.get_model(
        "loyalty",
        "EmissionCarte"
    )

    Annulation = apps.get_model(
        "loyalty",
        "Annulation"
    )

    JournalAudit = apps.get_model(
        "loyalty",
        "JournalAudit"
    )

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")

    User = apps.get_model(app_label, model_name)

    db_alias = schema_editor.connection.alias

    # 1. Creer la premiere succursale

    cafe_principal, _ = (
        Succursale.objects.using(db_alias).get_or_create(
            code="CAFE01",
            defaults={
                "nom": "Cafe principal",
                "adresse": "",
                "active": True,
            }
        )
    )

    # 2. Associer les achats historiques

    Achat.objects.using(db_alias).filter(
        succursale__isnull=True
    ).update(
        succursale_id=cafe_principal.pk
    )

    # 3. Associer les emissions de cartes

    EmissionCarte.objects.using(db_alias).filter(
        succursale__isnull=True
    ).update(
        succursale_id=cafe_principal.pk
    )

    # 4. Associer les annulations historiques

    Annulation.objects.using(db_alias).filter(
        succursale__isnull=True
    ).update(
        succursale_id=cafe_principal.pk
    )

    # 5. Associer les anciens journaux d'audit

    JournalAudit.objects.using(db_alias).filter(
        succursale__isnull=True
    ).update(
        succursale_id=cafe_principal.pk
    )

    # 6. Recuperer les employes de la V2

    employes = User.objects.using(db_alias).filter(
        groups__name__in=["Barista", "Gerant"]
    ).distinct()

    # 7. Affecter les employes au premier cafe

    for employe in employes:
        AffectationSuccursale.objects.using(
            db_alias
        ).get_or_create(
            employe_id=employe.pk,
            succursale_id=cafe_principal.pk,
            defaults={"active": True}
        )


class Migration(migrations.Migration):

    dependencies = [
        (
            "loyalty",
            "0014_ajouter_succursale_transactions"
        ),
    ]

    operations = [
        migrations.RunPython(
            migrer_donnees_v2,
            reverse_code=migrations.RunPython.noop
        ),
    ]