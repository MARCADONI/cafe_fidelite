
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from cafe_fidelite.loyalty.models import (
    Succursale,
    AffectationSuccursale,
    Client,
    Fidelite,
    Achat,
    EmissionCarte,
    RegleFidelite,
    MouvementFidelite,
)

from cafe_fidelite.loyalty.services import (
    obtenir_regle_fidelite,
    enregistrer_achat_payant,
    utiliser_recompense,
    emettre_carte_prepayee,
    utiliser_carte_prepayee,
)


class Command(BaseCommand):

    help = "Initialise les donnees de demonstration V3"

    @transaction.atomic
    def handle(self, *args, **options):

        User = get_user_model()

        # ==========================================
        # 1. CREATION DES GROUPES
        # ==========================================

        groupe_barista, _ = Group.objects.get_or_create(
            name="Barista"
        )

        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        groupe_proprietaire, _ = Group.objects.get_or_create(
            name="Proprietaire"
        )

        # ==========================================
        # 2. CREATION DES SUCCURSALES
        # ==========================================

        cafe1, _ = Succursale.objects.get_or_create(
            code="CAFE01",
            defaults={
                "nom": "Cafe principal",
                "adresse": "Chicoutimi",
                "active": True,
            },
        )

        cafe2, _ = Succursale.objects.get_or_create(
            code="CAFE02",
            defaults={
                "nom": "Cafe secondaire",
                "adresse": "Jonquiere",
                "active": True,
            },
        )

        if not cafe1.active or not cafe2.active:
            raise CommandError(
                "Les deux succursales doivent etre actives."
            )

        self.stdout.write(
            self.style.SUCCESS("Succursales disponibles.")
        )

        # ==========================================
        # 3. CREATION DES EMPLOYES
        # ==========================================

        def creer_employe(username, password, groupe, staff=False):

            utilisateur, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                },
            )

            if utilisateur.is_superuser:
                raise CommandError(
                    f"{username} est un superutilisateur."
                )

            utilisateur.set_password(password)
            utilisateur.is_active = True
            utilisateur.is_staff = staff
            utilisateur.save()

            utilisateur.groups.set([groupe])
            utilisateur.user_permissions.clear()

            return utilisateur

        barista = creer_employe(
            "barista_demo",
            "BaristaDemo2026!",
            groupe_barista,
        )

        gerant1 = creer_employe(
            "gerant_demo",
            "GerantDemo2026!",
            groupe_gerant,
        )

        gerant2 = creer_employe(
            "gerant2_demo",
            "Gerant2Demo2026!",
            groupe_gerant,
        )

        proprietaire = creer_employe(
            "proprietaire_demo",
            "ProprietaireDemo2026!",
            groupe_proprietaire,
            staff=True,
        )

        # ==========================================
        # 4. AFFECTATION DES EMPLOYES
        # ==========================================

        AffectationSuccursale.objects.filter(
            employe=gerant1
        ).exclude(
            succursale=cafe1
        ).update(active=False)

        AffectationSuccursale.objects.filter(
            employe=gerant2
        ).exclude(
            succursale=cafe2
        ).update(active=False)

        affectations = [
            (barista, cafe1),
            (barista, cafe2),
            (gerant1, cafe1),
            (gerant2, cafe2),
        ]

        for employe, succursale in affectations:

            AffectationSuccursale.objects.update_or_create(
                employe=employe,
                succursale=succursale,
                defaults={"active": True},
            )

        self.stdout.write(
            self.style.SUCCESS("Employes et affectations crees.")
        )

        # ==========================================
        # 5. REGLE DE FIDELITE
        # ==========================================

        maintenant = timezone.now()

        if not RegleFidelite.objects.filter(
            date_entree_vigueur__lte=maintenant
        ).exists():

            RegleFidelite.objects.create(
                seuil=10,
                date_entree_vigueur=(
                    maintenant - timedelta(days=30)
                ),
                cree_par=proprietaire,
            )

        regle = obtenir_regle_fidelite()

        # ==========================================
        # 6. CREATION DES CLIENTS
        # ==========================================

        client1, nouveau1 = Client.objects.get_or_create(
            telephone="4185550101",
            defaults={
                "nom": "Alice Demo V3",
                "courriel": "alice.v3@example.com",
            },
        )

        client2, nouveau2 = Client.objects.get_or_create(
            telephone="4185550102",
            defaults={
                "nom": "Jean Demo V3",
                "courriel": "jean.v3@example.com",
            },
        )

        client3, nouveau3 = Client.objects.get_or_create(
            telephone="4185550103",
            defaults={
                "nom": "Sophie Demo V3",
                "courriel": "sophie.v3@example.com",
            },
        )

        for client in [client1, client2, client3]:

            Fidelite.objects.get_or_create(client=client)

        # ==========================================
        # 7. TRANSACTIONS SUR PLUSIEURS JOURS
        # ==========================================

        def dater_achat(achat, jours):

            date_achat = maintenant - timedelta(days=jours)

            Achat.objects.filter(
                pk=achat.pk
            ).update(
                date_achat=date_achat
            )

            MouvementFidelite.objects.filter(
                achat=achat
            ).update(
                date_mouvement=date_achat
            )

        # Alice accumule des etampes dans les deux cafes.

        if nouveau1:

            for i in range(min(regle.seuil, 100)):

                succursale = cafe1 if i % 2 == 0 else cafe2

                achat = enregistrer_achat_payant(
                    client1,
                    employe=barista,
                    succursale=succursale,
                )

                dater_achat(achat, 5 - min(i, 4))

            fidelite = Fidelite.objects.get(client=client1)

            if fidelite.recompenses > 0:

                achat = utiliser_recompense(
                    client1,
                    employe=barista,
                    succursale=cafe2,
                )

                dater_achat(achat, 0)

        # Jean achete une carte au cafe 1
        # et l'utilise au cafe 2.

        if nouveau2:

            carte = emettre_carte_prepayee(
                client2,
                employe=barista,
                succursale=cafe1,
            )

            date_emission = maintenant - timedelta(days=4)

            type(carte).objects.filter(
                pk=carte.pk
            ).update(
                date_emission=date_emission
            )

            EmissionCarte.objects.filter(
                carte=carte
            ).update(
                date_emission=date_emission
            )

            for jours in [3, 2, 1]:

                achat = utiliser_carte_prepayee(
                    carte,
                    employe=barista,
                    succursale=cafe2,
                )

                dater_achat(achat, jours)

        # Sophie effectue des achats payants
        # dans les deux succursales.

        if nouveau3:

            for succursale, jours in [
                (cafe1, 3),
                (cafe1, 2),
                (cafe2, 1),
            ]:

                achat = enregistrer_achat_payant(
                    client3,
                    employe=barista,
                    succursale=succursale,
                )

                dater_achat(achat, jours)

        # ==========================================
        # 8. AFFICHAGE DU RESULTAT
        # ==========================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Donnees de demonstration V3 initialisees."
            )
        )

        self.stdout.write(
            f"Succursales : {Succursale.objects.count()}"
        )

        self.stdout.write(
            f"Clients : {Client.objects.count()}"
        )

        self.stdout.write(
            f"Achats : {Achat.objects.count()}"
        )

        self.stdout.write(
            f"Emissions : {EmissionCarte.objects.count()}"
        )

        self.stdout.write("")
        self.stdout.write("Comptes de demonstration :")
        self.stdout.write("barista_demo")
        self.stdout.write("gerant_demo")
        self.stdout.write("gerant2_demo")
        self.stdout.write("proprietaire_demo")
