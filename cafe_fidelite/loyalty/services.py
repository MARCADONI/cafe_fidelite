from .models import Achat
from .models import Client
from .models import Fidelite
from .models import CartePrepayee

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Achat, Fidelite, RegleFidelite,Annulation,MouvementFidelite,CartePrepayee,EmissionCarte




@transaction.atomic
def enregistrer_achat_payant(client, employe=None):
    """
    Enregistre un achat payant et memorise
    ses effets sur les compteurs de fidelite.
    """

    if client.est_anonymise or client.est_fusionne:
        raise ValueError(
            "Ce client ne peut plus effectuer d'achats."
        )

    if employe is not None and not employe.is_authenticated:
        raise ValueError("Employe non authentifie.")

    regle = obtenir_regle_fidelite()
    seuil = regle.seuil

    fidelite, _ = Fidelite.objects.get_or_create(
        client=client
    )

    fidelite = (
        Fidelite.objects
        .select_for_update()
        .get(pk=fidelite.pk)
    )

    etampes_ajoutees = 0
    dette_remboursee = 0
    recompenses_generees = 0

    if fidelite.dette_etampes > 0:
        fidelite.dette_etampes -= 1
        dette_remboursee = 1
    else:
        fidelite.progression += 1
        etampes_ajoutees = 1

    while fidelite.progression >= seuil:
        fidelite.progression -= seuil
        fidelite.recompenses += 1
        recompenses_generees += 1

    achat = Achat.objects.create(
        client=client,
        type_achat=Achat.TypeAchat.PAYANT,
        employe=employe,
        seuil_fidelite_applique=seuil,
        etampes_ajoutees=etampes_ajoutees,
        dette_remboursee=dette_remboursee,
        recompenses_generees=recompenses_generees,
        effets_traces=True,
    )

    if dette_remboursee:
        MouvementFidelite.objects.create(
            client=client,
            achat=achat,
            type_mouvement=(
                MouvementFidelite.TypeMouvement.ACHAT
            ),
            variation_dette=-dette_remboursee,
    )

    if etampes_ajoutees:
        MouvementFidelite.objects.create(
            client=client,
            achat=achat,
            type_mouvement=(
                MouvementFidelite.TypeMouvement.ACHAT
            ),
            variation_etampes=etampes_ajoutees,
        )

    if recompenses_generees:
        MouvementFidelite.objects.create(
            client=client,
            achat=achat,
            type_mouvement=(
                MouvementFidelite.TypeMouvement.CONVERSION
            ),
            variation_etampes=(
                -recompenses_generees * seuil
            ),
        variation_recompenses=recompenses_generees,
    )

    fidelite.save(
    update_fields=[
        "progression",
        "recompenses",
        "dette_etampes",
    ]
    )

    return achat



@transaction.atomic
def utiliser_recompense(client, employe=None):
    """
    Utilise une recompense pour offrir
    un cafe gratuit au client.

    Conserve l'achat et le mouvement
    dans l'historique.
    """

    if client.est_anonymise or client.est_fusionne:
        raise ValueError(
            "Ce client ne peut plus effectuer d'operations."
        )

    if employe is not None and not employe.is_authenticated:
        raise ValueError(
            "L'employe doit etre authentifie."
        )

    fidelite = (
        Fidelite.objects
        .select_for_update()
        .get(client=client)
    )

    if fidelite.recompenses < 1:
        raise ValueError(
            "Le client ne possede aucune recompense."
        )

    fidelite.recompenses -= 1
    fidelite.save(update_fields=["recompenses"])

    achat = Achat.objects.create(
        client=client,
        type_achat=Achat.TypeAchat.GRATUIT_FIDELITE,
        employe=employe,
        effets_traces=True,
    )

    MouvementFidelite.objects.create(
        client=client,
        achat=achat,
        type_mouvement=(
            MouvementFidelite.TypeMouvement.UTILISATION
        ),
        variation_recompenses=-1,
        commentaire="Utilisation d'une recompense",
    )

    return achat



@transaction.atomic
def emettre_carte_prepayee(client, employe=None):
    """
    Emet une carte prepayee de 11 cafes
    et conserve la transaction de vente.
    """

    if client.est_anonymise or client.est_fusionne:
        raise ValueError(
            "Ce client ne peut plus recevoir de carte."
        )

    if employe is not None and not employe.is_authenticated:
        raise ValueError(
            "Employe non authentifie."
        )

    carte = CartePrepayee.objects.create(
        client=client,
        cafes_restants=11,
        active=True,
        est_annulee=False,
        est_cloturee=False,
    )

    EmissionCarte.objects.create(
        carte=carte,
        employe=employe,
        date_emission=carte.date_emission,
        annulee=False,
    )

    return carte


@transaction.atomic
def utiliser_carte_prepayee(carte, employe=None):
    """
    Consomme un cafe sur une carte prepayee.
    """

    if employe is not None and not employe.is_authenticated:
        raise ValueError(
            "Employe non authentifie."
        )

    # Une mise a jour conditionnelle empeche
    # de consommer une carte invalide ou vide.
    lignes_modifiees = (
        CartePrepayee.objects
        .filter(
            pk=carte.pk,
            active=True,
            est_annulee=False,
            est_cloturee=False,
            cafes_restants__gt=0,
            client__est_anonymise=False,
            client__est_fusionne=False,
        )
        .update(
            cafes_restants=F("cafes_restants") - 1
        )
    )

    if lignes_modifiees != 1:
        raise ValueError(
            "Carte inactive, invalide ou sans credit."
        )

    achat = Achat.objects.create(
        client=carte.client,
        type_achat=Achat.TypeAchat.PREPAYE,
        carte_prepayee=carte,
        employe=employe,
        effets_traces=True,
    )

    return achat



def obtenir_regle_fidelite(date_operation=None):
    """
    Retourne la regle de fidelite applicable
    a la date de l'operation.
    """

    if date_operation is None:
        date_operation = timezone.now()

    regle = (
        RegleFidelite.objects
        .filter(
            date_entree_vigueur__lte=date_operation
        )
        .order_by("-date_entree_vigueur")
        .first()
    )

    if regle is None:
        raise ValueError(
            "Aucune regle de fidelite applicable. "
            "Verifiez la migration des donnees v2."
        )

    return regle


@transaction.atomic
def programmer_regle_fidelite(
    seuil,
    date_entree_vigueur,
    gerant,
):
    """
    Programme un nouveau seuil de fidelite.
    """

    if not gerant.is_authenticated:
        raise PermissionError(
            "Connexion requise."
        )

    if not gerant.groups.filter(
        name="gerant"
    ).exists():
        raise PermissionError(
            "Seul un gerant peut modifier les regles."
        )

    if seuil < 1:
        raise ValueError(
            "Le seuil doit etre superieur a zero."
        )

    if timezone.is_naive(date_entree_vigueur):
        raise ValueError(
            "La date doit inclure un fuseau horaire."
        )

    if date_entree_vigueur <= timezone.now():
        raise ValueError(
            "La date d'entree en vigueur doit etre future."
        )

    return RegleFidelite.objects.create(
        seuil=seuil,
        date_entree_vigueur=date_entree_vigueur,
        cree_par=gerant,
    )





@transaction.atomic
def annuler_achat_payant(achat_id, gerant, motif):
    """
    Annule un achat payant v2 sans
    recompense generee.

    Enregistre un mouvement compensatoire.
    """

    if not gerant.is_authenticated:
        raise PermissionError(
            "Connexion requise."
        )

    if not (
        gerant.is_superuser
        or gerant.groups.filter(name="gerant").exists()
    ):
        raise PermissionError(
            "Seul un gerant peut annuler un achat."
        )

    if not motif or not motif.strip():
        raise ValueError(
            "Le motif est obligatoire."
        )

    achat = (
        Achat.objects
        .select_for_update()
        .get(pk=achat_id)
    )

    if achat.type_achat != Achat.TypeAchat.PAYANT:
        raise ValueError(
            "Cet achat n'est pas un achat payant."
        )

    if not achat.effets_traces:
        raise ValueError(
            "Impossible d'annuler automatiquement "
            "cet achat historique v1."
        )

    if Annulation.objects.filter(achat=achat).exists():
        raise ValueError(
            "Cet achat a deja ete annule."
        )

    fidelite = (
        Fidelite.objects
        .select_for_update()
        .get(client=achat.client)
    )

    variation_etampes, variation_dette = (
        appliquer_correction_achat_simple(
            fidelite,
            achat,
        )
    )

    
    fidelite.save(
        update_fields=[
            "progression",
            "recompenses",
            "dette_etampes",
        ]
    )


    annulation = Annulation.objects.create(
        achat=achat,
        gerant=gerant,
        motif=motif.strip(),
    )

    MouvementFidelite.objects.create(
        client=achat.client,
        achat=achat,
        annulation=annulation,
        type_mouvement=(
            MouvementFidelite.TypeMouvement.ANNULATION
        ),
        variation_etampes=variation_etampes,
        variation_dette=variation_dette,
        commentaire="Correction d'un achat payant",
    )

    return annulation



def retirer_etampes_avec_dette(fidelite, quantite):
    """
    Retire des etampes du solde disponible.

    Si le solde est insuffisant, la difference
    devient une dette d'etampes.
    """

    if quantite < 0:
        raise ValueError(
            "La quantite doit etre positive."
        )

    etampes_disponibles = fidelite.progression

    etampes_retirees = min(
        etampes_disponibles,
        quantite
    )

    fidelite.progression -= etampes_retirees

    manque = quantite - etampes_retirees

    if manque > 0:
        fidelite.dette_etampes += manque




def appliquer_correction_achat_simple(fidelite, achat):
    """
    Annule les effets d'un achat payant v2.

    Si la recompense generee est encore
    disponible, elle est reconvertie en etampes.

    Si elle n'est plus disponible, l'operation
    est refusee pour reconciliation ulterieure.
    """

    variation_etampes = 0
    variation_dette = 0

    if achat.recompenses_generees > 0:
        if (
            fidelite.recompenses
            < achat.recompenses_generees
        ):
            raise ValueError(
                "Recompense deja consommee : "
                "reconciliation necessaire."
            )

        seuil = achat.seuil_fidelite_applique

        if not seuil:
            raise ValueError(
                "Seuil de fidelite introuvable."
            )

        fidelite.recompenses -= (
            achat.recompenses_generees
        )

        etampes_restituees = (
            achat.recompenses_generees * seuil
        )

        fidelite.progression += etampes_restituees
        variation_etampes += etampes_restituees

    if achat.dette_remboursee:
        fidelite.dette_etampes += (
            achat.dette_remboursee
        )

        variation_dette += (
            achat.dette_remboursee
        )

    if achat.etampes_ajoutees:
        disponibles = min(
            fidelite.progression,
            achat.etampes_ajoutees,
        )

        fidelite.progression -= disponibles
        variation_etampes -= disponibles

        manque = (
            achat.etampes_ajoutees - disponibles
        )

        if manque:
            fidelite.dette_etampes += manque
            variation_dette += manque

    return variation_etampes, variation_dette



@transaction.atomic
def annuler_utilisation_recompense(
    achat_id,
    gerant,
    motif,
):
    """
    Annule l'utilisation d'une recompense
    et restitue une recompense au client.
    """

    if not gerant.is_authenticated:
        raise PermissionError(
            "Connexion requise."
        )

    if not (
        gerant.is_superuser
        or gerant.groups.filter(name="gerant").exists()
    ):
        raise PermissionError(
            "Seul un gerant peut annuler une transaction."
        )

    if not motif or not motif.strip():
        raise ValueError(
            "Le motif d'annulation est obligatoire."
        )

    achat = (
        Achat.objects
        .select_for_update()
        .get(pk=achat_id)
    )

    if (
        achat.type_achat
        != Achat.TypeAchat.GRATUIT_FIDELITE
    ):
        raise ValueError(
            "Cet achat n'est pas un cafe gratuit."
        )

    if not achat.effets_traces:
        raise ValueError(
            "Cette transaction historique necessite "
            "une verification specifique."
        )

    if Annulation.objects.filter(achat=achat).exists():
        raise ValueError(
            "Cette transaction a deja ete annulee."
        )

    fidelite = (
        Fidelite.objects
        .select_for_update()
        .get(client=achat.client)
    )

    fidelite.recompenses += 1
    fidelite.save(update_fields=["recompenses"])

    annulation = Annulation.objects.create(
        achat=achat,
        gerant=gerant,
        motif=motif.strip(),
    )

    
    
    MouvementFidelite.objects.create(
        client=achat.client,
        achat=achat,
        annulation=annulation,
        type_mouvement=(
            MouvementFidelite.TypeMouvement.ANNULATION
        ),
        variation_recompenses=1,
        commentaire="Annulation d'un cafe gratuit",
    )



    return annulation



@transaction.atomic
def annuler_utilisation_carte(
    achat_id,
    gerant,
    motif,
):
    """
    Annule un cafe consomme sur une carte
    et restitue un credit.
    """

    if not gerant.is_authenticated:
        raise PermissionError(
            "Connexion requise."
        )

    if not (
        gerant.is_superuser
        or gerant.groups.filter(name="gerant").exists()
    ):
        raise PermissionError(
            "Seul un gerant peut annuler une transaction."
        )

    if not motif or not motif.strip():
        raise ValueError(
            "Le motif est obligatoire."
        )

    achat = (
        Achat.objects
        .select_for_update()
        .get(pk=achat_id)
    )

    if achat.type_achat != Achat.TypeAchat.PREPAYE:
        raise ValueError(
            "Cet achat n'est pas un cafe prepaye."
        )

    if not achat.effets_traces:
        raise ValueError(
            "Cette transaction historique necessite "
            "une verification specifique."
        )

    if Annulation.objects.filter(achat=achat).exists():
        raise ValueError(
            "Cette consommation a deja ete annulee."
        )

    carte = (
        CartePrepayee.objects
        .select_for_update()
        .get(pk=achat.carte_prepayee_id)
    )

    if carte.est_annulee or carte.est_cloturee:
        raise ValueError(
            "Impossible de restituer le credit "
            "sur une carte annulee ou cloturee."
        )

    carte.cafes_restants = F("cafes_restants") + 1
    carte.active = True

    carte.save(
        update_fields=[
            "cafes_restants",
            "active",
        ]
    )

    annulation = Annulation.objects.create(
        achat=achat,
        gerant=gerant,
        motif=motif.strip(),
    )

    return annulation


@transaction.atomic
def annuler_vente_carte(
    emission_id,
    gerant,
    motif,
):
    """
    Annule la vente d'une carte prepayee
    uniquement si aucun cafe n'a ete consomme.
    """

    if not gerant.is_authenticated:
        raise PermissionError(
            "Connexion requise."
        )

    if not (
        gerant.is_superuser
        or gerant.groups.filter(name="gerant").exists()
    ):
        raise PermissionError(
            "Seul un gerant peut annuler une vente."
        )

    if not motif or not motif.strip():
        raise ValueError(
            "Le motif est obligatoire."
        )

    emission = (
        EmissionCarte.objects
        .select_for_update()
        .get(pk=emission_id)
    )

    if emission.annulee:
        raise ValueError(
            "Cette vente est deja annulee."
        )

    carte = (
        CartePrepayee.objects
        .select_for_update()
        .get(pk=emission.carte_id)
    )

    if carte.est_annulee or carte.est_cloturee:
        raise ValueError(
            "Cette carte n'est plus annulable."
        )

    # Toute consommation historique ou actuelle
    # doit etre examinee avant d'annuler la vente.
    if Achat.objects.filter(
        carte_prepayee=carte,
        type_achat=Achat.TypeAchat.PREPAYE,
    ).exists():
        raise ValueError(
            "Cette carte possede un historique "
            "de consommation."
        )

    if carte.cafes_restants != 11:
        raise ValueError(
            "Le solde de la carte est different "
            "du solde initial."
        )

    if Annulation.objects.filter(
        emission_carte=emission
    ).exists():
        raise ValueError(
            "Cette vente a deja ete annulee."
        )

    carte.est_annulee = True
    carte.active = False

    carte.save(
        update_fields=[
            "est_annulee",
            "active",
        ]
    )

    emission.annulee = True
    emission.save(update_fields=["annulee"])

    annulation = Annulation.objects.create(
        emission_carte=emission,
        gerant=gerant,
        motif=motif.strip(),
    )

    return annulation
