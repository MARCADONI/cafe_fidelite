
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from cafe_fidelite.loyalty.models import (
    Client,
    Fidelite,
    Succursale,
    Achat,
    EmissionCarte,
)


class Command(BaseCommand):

    help = (
        "Affiche les soldes de fidelite et les cartes "
        "prepayees des clients, par succursale ou pour le reseau."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "--succursale",
            type=str,
            help="Code de la succursale, par exemple CAFE01.",
        )

    def handle(self, *args, **options):

        code_succursale = options.get("succursale")

        clients = (
            Client.objects
            .all()
            .order_by("id")
            .prefetch_related("cartes_prepayees")
        )

        # ==========================================
        # 1. FILTRAGE PAR SUCCURSALE
        # ==========================================

        if code_succursale:

            succursale = Succursale.objects.filter(
                code__iexact=code_succursale
            ).first()

            if succursale is None:
                raise CommandError(
                    f"Succursale inconnue : {code_succursale}"
                )

            clients_achats = Achat.objects.filter(
                succursale=succursale
            ).values_list("client_id", flat=True)

            clients_cartes = EmissionCarte.objects.filter(
                succursale=succursale
            ).values_list("carte__client_id", flat=True)

            clients = clients.filter(
                Q(id__in=clients_achats)
                | Q(id__in=clients_cartes)
            ).distinct()

            self.stdout.write(
                f"===== SUCCURSALE {succursale.code} ====="
            )

            self.stdout.write(
                f"Nom : {succursale.nom}"
            )

        else:

            self.stdout.write(
                "===== ENSEMBLE DU RESEAU ====="
            )

        self.stdout.write(
            "Les soldes affiches sont globaux au reseau."
        )

        # ==========================================
        # 2. VERIFICATION DES CLIENTS
        # ==========================================

        if not clients.exists():

            self.stdout.write("Aucun client trouve.")
            return

        self.stdout.write(
            "===== SOLDES DES CLIENTS ====="
        )

        # ==========================================
        # 3. AFFICHAGE DES SOLDES
        # ==========================================

        for client in clients:

            fidelite = Fidelite.objects.filter(
                client=client
            ).first()

            progression = (
                fidelite.progression if fidelite else 0
            )

            recompenses = (
                fidelite.recompenses if fidelite else 0
            )

            dette = (
                fidelite.dette_etampes if fidelite else 0
            )

            self.stdout.write("")

            self.stdout.write(
                f"Client #{client.id} - {client.nom}"
            )

            self.stdout.write(
                f"  Etampes : {progression}"
            )

            self.stdout.write(
                f"  Recompenses disponibles : {recompenses}"
            )

            self.stdout.write(
                f"  Dette d'etampes : {dette}"
            )

            # ======================================
            # 4. CARTES PREPAYEES
            # ======================================

            cartes = list(
                client.cartes_prepayees.all()
            )

            if not cartes:

                self.stdout.write(
                    "  Cartes prepayees : aucune"
                )

            else:

                self.stdout.write(
                    "  Cartes prepayees :"
                )

                for carte in cartes:

                    self.stdout.write(
                        f"    Carte #{carte.id} : "
                        f"{carte.cafes_restants} cafes restants "
                        f"(active={carte.active})"
                    )

        # ==========================================
        # 5. RESULTAT FINAL
        # ==========================================

        self.stdout.write("")

        self.stdout.write(
            f"Nombre de clients : {clients.count()}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Affichage des soldes termine."
            )
        )
