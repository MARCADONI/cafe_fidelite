from django.core.exceptions import PermissionDenied

from .models import Succursale


ROLE_BARISTA = "Barista"
ROLE_GERANT = "Gerant"
ROLE_PROPRIETAIRE = "Proprietaire"


def est_proprietaire(utilisateur):
    """
    Verifie si l'utilisateur possede le role Proprietaire.
    """

    return (
        utilisateur is not None
        and utilisateur.is_authenticated
        and utilisateur.is_active
        and utilisateur.groups.filter(
            name=ROLE_PROPRIETAIRE
        ).exists()
    )


def est_gerant(utilisateur):
    """
    Verifie si l'utilisateur possede le role Gerant.
    """

    return (
        utilisateur is not None
        and utilisateur.is_authenticated
        and utilisateur.is_active
        and utilisateur.groups.filter(
            name=ROLE_GERANT
        ).exists()
    )


def est_employe(utilisateur):
    """
    Verifie si l'utilisateur possede un role metier.
    """

    return (
        utilisateur is not None
        and utilisateur.is_authenticated
        and utilisateur.is_active
        and utilisateur.groups.filter(
            name__in=[
                ROLE_BARISTA,
                ROLE_GERANT,
                ROLE_PROPRIETAIRE,
            ]
        ).exists()
    )


def obtenir_succursales_autorisees(utilisateur):
    """
    Retourne les succursales actives accessibles
    par l'utilisateur.
    """

    if not est_employe(utilisateur):
        return Succursale.objects.none()

    if est_proprietaire(utilisateur):
        return Succursale.objects.filter(
            active=True
        )

    succursales = Succursale.objects.filter(
        active=True,
        affectations_employes__employe=utilisateur,
        affectations_employes__active=True,
    ).distinct()

    # Un gerant doit avoir une seule succursale active.
    if est_gerant(utilisateur):
        if succursales.count() != 1:
            return Succursale.objects.none()

    return succursales


def verifier_acces_succursale(
    utilisateur,
    succursale
):
    """
    Verifie que l'utilisateur peut effectuer
    une operation dans cette succursale.
    """

    if not est_employe(utilisateur):
        raise PermissionDenied(
            "Utilisateur non autorise."
        )

    if succursale is None:
        raise PermissionDenied(
            "Aucune succursale selectionnee."
        )

    if not obtenir_succursales_autorisees(
        utilisateur
    ).filter(pk=succursale.pk).exists():

        raise PermissionDenied(
            "Vous ne pouvez pas acceder "
            "a cette succursale."
        )

    return succursale


def obtenir_succursale_active(
    utilisateur,
    succursale_id=None
):
    """
    Recupere la succursale selectionnee.

    Si une seule succursale est autorisee,
    elle est selectionnee automatiquement.
    """

    succursales = obtenir_succursales_autorisees(
        utilisateur
    )

    if succursale_id is not None:

        succursale = succursales.filter(
            pk=succursale_id
        ).first()

        if succursale is None:
            raise PermissionDenied(
                "Succursale non autorisee."
            )

        return succursale

    if succursales.count() == 1:
        return succursales.first()

    raise PermissionDenied(
        "Veuillez selectionner une succursale "
        "autorisee."
    )


def verifier_permission_annulation(
    utilisateur,
    succursale
):
    """
    Autorise uniquement un gerant de la succursale
    ou un proprietaire a annuler une transaction.
    """

    if not (
        est_gerant(utilisateur)
        or est_proprietaire(utilisateur)
    ):
        raise PermissionDenied(
            "Seul un gerant ou un proprietaire "
            "peut annuler une transaction."
        )

    return verifier_acces_succursale(
        utilisateur,
        succursale
    )

def obtenir_succursale_session(request):
    """
    Retourne la succursale active de la session
    apres verification des permissions.
    """

    succursale_id = request.session.get(
        "succursale_active_id"
    )

    try:

        succursale = obtenir_succursale_active(
            request.user,
            succursale_id
        )

    except PermissionDenied:

        request.session.pop(
            "succursale_active_id",
            None
        )

        raise

    request.session["succursale_active_id"] = (
        succursale.pk
    )

    return succursale