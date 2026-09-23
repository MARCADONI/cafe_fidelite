from .models import Achat
from .models import Client
from .models import Fidelite
from .models import CartePrepayee


def enregistrer_achat_payant(client: Client):
    fidelite, _ = Fidelite.objects.get_or_create(client=client)

    Achat.objects.create(
        client=client,
        type_achat=Achat.TypeAchat.PAYANT,
    )

    fidelite.progression += 1

    if fidelite.progression >= 10:
        fidelite.progression -= 10
        fidelite.recompenses += 1

    fidelite.save()

    return fidelite

def utiliser_recompense(client: Client):
    fidelite, _ = Fidelite.objects.get_or_create(client=client)

    if fidelite.recompenses <= 0:
        return None

    achat = Achat.objects.create(
        client=client,
        type_achat=Achat.TypeAchat.GRATUIT_FIDELITE,
    )

    fidelite.recompenses -= 1
    fidelite.save()

    return achat

def emettre_carte_prepayee(client: Client):
    carte = CartePrepayee.objects.create(
        client=client,
        cafes_restants=11,
        active=True,
    )

    return carte

def utiliser_carte_prepayee(carte: CartePrepayee):
    if not carte.active or carte.cafes_restants <= 0:
        return None

    achat = Achat.objects.create(
        client=carte.client,
        type_achat=Achat.TypeAchat.PREPAYE,
        carte_prepayee=carte,
    )

    carte.cafes_restants -= 1

    if carte.cafes_restants == 0:
        carte.active = False

    carte.save()

    return achat