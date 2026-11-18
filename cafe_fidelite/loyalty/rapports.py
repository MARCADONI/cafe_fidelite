from datetime import datetime, time, timedelta

from django.utils import timezone

from .models import Achat, EmissionCarte


def generer_rapport(date_debut, date_fin, succursale=None):
    """
    Calcule les statistiques nettes pour une periode.

    Si une succursale est fournie :
        rapport de cette succursale.

    Si succursale=None :
        rapport global du reseau.

    Les transactions annulees sont exclues.
    """

    if date_debut > date_fin:
        raise ValueError(
            "La date de debut doit preceder "
            "la date de fin."
        )

    # 1. Determiner les bornes horaires

    fuseau = timezone.get_current_timezone()

    debut = timezone.make_aware(
        datetime.combine(date_debut, time.min),
        fuseau,
    )

    fin_exclusive = timezone.make_aware(
        datetime.combine(
            date_fin + timedelta(days=1),
            time.min,
        ),
        fuseau,
    )

    # 2. Recuperer les achats non annules

    achats = Achat.objects.filter(
        date_achat__gte=debut,
        date_achat__lt=fin_exclusive,
        annulation__isnull=True,
    )

    # 3. Recuperer les ventes non annulees

    emissions = EmissionCarte.objects.filter(
        date_emission__gte=debut,
        date_emission__lt=fin_exclusive,
        annulation__isnull=True,
        annulee=False,
    )

    # 4. Filtrer par succursale

    if succursale is not None:

        achats = achats.filter(
            succursale=succursale
        )

        emissions = emissions.filter(
            succursale=succursale
        )

    # 5. Calculer les statistiques

    cafes_payants = achats.filter(
        type_achat=Achat.TypeAchat.PAYANT
    ).count()

    cafes_gratuits = achats.filter(
        type_achat=Achat.TypeAchat.GRATUIT_FIDELITE
    ).count()

    cafes_prepayes = achats.filter(
        type_achat=Achat.TypeAchat.PREPAYE
    ).count()

    cartes_vendues = emissions.count()

    total_cafes = (
        cafes_payants
        + cafes_gratuits
        + cafes_prepayes
    )

    # 6. Retourner le rapport

    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "succursale": succursale,
        "cafes_payants": cafes_payants,
        "cafes_gratuits": cafes_gratuits,
        "cafes_prepayes": cafes_prepayes,
        "cartes_vendues": cartes_vendues,
        "total_cafes": total_cafes,
    }