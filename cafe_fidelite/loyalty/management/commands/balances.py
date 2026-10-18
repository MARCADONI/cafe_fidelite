
from django.core.management.base import BaseCommand

from cafe_fidelite.loyalty.models import Client, Fidelite


class Command(BaseCommand):
    help = "Affiche les soldes de fidelite et les cartes prepayees des clients."

    def handle(self, *args, **options):

        clients = (
            Client.objects
            .all()
            .order_by("id")
            .prefetch_related("cartes_prepayees")
        )

        if not clients.exists():
            self.stdout.write("Aucun client trouve.")
            return

        self.stdout.write("===== SOLDES DES CLIENTS =====")

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

            cartes = list(client.cartes_prepayees.all())

            if not cartes:
                self.stdout.write(
                    "  Cartes prepayees : aucune"
                )
            else:
                self.stdout.write("  Cartes prepayees :")

                for carte in cartes:
                    self.stdout.write(
                        f"    Carte #{carte.id} : "
                        f"{carte.cafes_restants} cafes restants "
                        f"(active={carte.active})"
                    )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Affichage des soldes termine."
            )
        )
