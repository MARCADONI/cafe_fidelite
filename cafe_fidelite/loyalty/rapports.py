
from datetime import datetime, time, timedelta

from django.utils import timezone

from .models import Achat, EmissionCarte


def generer_rapport(date_debut, date_fin):
    """
    Calcule les statistiques nettes du cafe
    pour une periode inclusive.

    Les transactions annulees sont exclues.
    """

    if date_debut > date_fin:
        raise ValueError(
            "La date de debut doit preceder "
            "la date de fin."
        )

    # Bornes horaires dans le fuseau Django.
    # La borne de fin est exclusive.
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

    achats = Achat.objects.filter(
        date_achat__gte=debut,
        date_achat__lt=fin_exclusive,
        annulation__isnull=True,
    )

    cafes_payants = achats.filter(
        type_achat=Achat.TypeAchat.PAYANT
    ).count()

    cafes_gratuits = achats.filter(
        type_achat=Achat.TypeAchat.GRATUIT_FIDELITE
    ).count()

    cafes_prepayes = achats.filter(
        type_achat=Achat.TypeAchat.PREPAYE
    ).count()

    cartes_vendues = EmissionCarte.objects.filter(
        date_emission__gte=debut,
        date_emission__lt=fin_exclusive,
        annulation__isnull=True,
        annulee=False,
    ).count()

    return {
        "date_debut": date_debut,
        "date_fin": date_fin,
        "cafes_payants": cafes_payants,
        "cafes_gratuits": cafes_gratuits,
        "cafes_prepayes": cafes_prepayes,
        "cartes_vendues": cartes_vendues,
    }
