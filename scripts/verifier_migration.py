
import json

from django.contrib.auth import get_user_model

from cafe_fidelite.loyalty.models import (
    Client,
    Fidelite,
    CartePrepayee,
    Achat,
    EmissionCarte,
    Annulation,
    MouvementFidelite,
    JournalAudit,
    RegleFidelite,
    Succursale,
    AffectationSuccursale,
    FusionClient,
)


def verifier_migration():
    User = get_user_model()

    modeles = [
        User,
        Client,
        Fidelite,
        CartePrepayee,
        Achat,
        EmissionCarte,
        Annulation,
        MouvementFidelite,
        JournalAudit,
        RegleFidelite,
        Succursale,
        AffectationSuccursale,
        FusionClient,
    ]

    rapport = {
        "compteurs": {
            modele.__name__: modele.objects.count()
            for modele in modeles
        },
        "fidelite": list(
            Fidelite.objects.order_by("id").values(
                "id",
                "client_id",
                "client__nom",
                "progression",
                "recompenses",
                "dette_etampes",
            )
        ),
        "cartes": list(
            CartePrepayee.objects.order_by("id").values(
                "id",
                "client_id",
                "cafes_restants",
                "active",
                "est_annulee",
                "est_cloturee",
            )
        ),
        "achats": list(
            Achat.objects.order_by("id").values(
                "id",
                "client_id",
                "succursale__code",
                "type_achat",
                "carte_prepayee_id",
            )
        ),
        "emissions": list(
            EmissionCarte.objects.order_by("id").values(
                "id",
                "carte_id",
                "succursale__code",
                "annulee",
            )
        ),
        "annulations": list(
            Annulation.objects.order_by("id").values(
                "id",
                "achat_id",
                "emission_carte_id",
                "succursale__code",
            )
        ),
        "succursales": list(
            Succursale.objects.order_by("id").values(
                "id",
                "code",
                "nom",
                "active",
            )
        ),
    }

    print(
        json.dumps(
            rapport,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
            default=str,
        )
    )


verifier_migration()
