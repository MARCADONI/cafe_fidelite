from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404

from .models import Succursale
from .forms import ClientForm
from .forms import AnnulationTransactionForm
from .models import CartePrepayee, Client, Fidelite,JournalAudit,Achat, EmissionCarte
from .services import (
    emettre_carte_prepayee,
    enregistrer_achat_payant,
    utiliser_carte_prepayee,
    utiliser_recompense,
    annuler_achat_payant,
    annuler_utilisation_recompense,
    annuler_utilisation_carte,
    annuler_vente_carte,
)

from .services_succursales import (
    est_employe,
    est_gerant,
    est_proprietaire,
    obtenir_succursales_autorisees,
    obtenir_succursale_active,
    obtenir_succursale_session,

)

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render,redirect

from .forms import RapportStatistiquesForm
from .rapports import generer_rapport

from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from cafe_fidelite.loyalty.forms import FusionClientForm
from cafe_fidelite.loyalty.services import fusionner_clients

from cafe_fidelite.loyalty.forms import AnonymisationClientForm
from cafe_fidelite.loyalty.services import anonymiser_client

from functools import wraps


def employe_required(view_func):
    """
    Autorise les baristas, les gerants
    et les proprietaires.
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not est_employe(request.user):
            raise PermissionDenied(
                "Vous ne possedez pas les droits requis."
            )

        if not obtenir_succursales_autorisees(
            request.user
        ).exists():
            raise PermissionDenied(
                "Aucune succursale autorisee."
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper

def gerant_required(view_func):
    """
    Autorise les gerants et les proprietaires.
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not (
            est_gerant(request.user)
            or est_proprietaire(request.user)
        ):
            raise PermissionDenied(
                "Acces reserve aux gerants "
                "et aux proprietaires."
            )

        if not est_proprietaire(request.user):

            if not obtenir_succursales_autorisees(
                request.user
            ).exists():
                raise PermissionDenied(
                    "Aucune succursale autorisee."
                )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper

def succursale_required(view_func):
    """
    Exige une succursale active et autorisee.
    """

    @employe_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        try:

            request.succursale = (
                obtenir_succursale_session(request)
            )

        except PermissionDenied:

            if request.method != "GET":
                raise

            return redirect(
                "loyalty:choisir_succursale"
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper

@employe_required
def choisir_succursale(request):
    """
    Permet a un employe de selectionner
    sa succursale active.
    """

    succursales = obtenir_succursales_autorisees(
        request.user
    )

    if request.method == "POST":

        try:

            succursale_id = int(
                request.POST.get("succursale_id", "")
            )

        except (TypeError, ValueError):

            raise PermissionDenied(
                "Identifiant de succursale invalide."
            )

        succursale = obtenir_succursale_active(
            request.user,
            succursale_id
        )

        request.session["succursale_active_id"] = (
            succursale.pk
        )

        return redirect(
            "loyalty:client_recherche_creation"
        )

    # Selection automatique si un seul cafe

    if succursales.count() == 1:

        succursale = succursales.first()

        request.session["succursale_active_id"] = (
            succursale.pk
        )

        return redirect(
            "loyalty:client_recherche_creation"
        )

    return render(
        request,
        "loyalty/choisir_succursale.html",
        {
            "succursales": succursales,
            "succursale_active_id": request.session.get(
                "succursale_active_id"
            ),
        }
    )

@succursale_required
def client_recherche_creation(request):
    telephone = request.GET.get("telephone", "")
    client = None

    # Création d'un nouveau client
    if request.method == "POST":
        formulaire = ClientForm(request.POST)

        if formulaire.is_valid():
            client_cree = formulaire.save()

            messages.success(
                request,
                f"Le client {client_cree.nom} a été créé avec succès.",
            )

            return redirect("loyalty:client_recherche_creation")
    else:
        formulaire = ClientForm()

    # Recherche d'un client existant
    if telephone:
        client = Client.objects.filter(telephone=telephone).first()

    contexte = {
        "telephone": telephone,
        "client": client,
        "formulaire": formulaire,
    }

    return render(
        request,
        "loyalty/client_recherche_creation.html",
        contexte,
    )

def proprietaire_required(view_func):
    """
    Autorise uniquement les proprietaires.
    """

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not est_proprietaire(request.user):
            raise PermissionDenied(
                "Acces reserve aux proprietaires."
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


@succursale_required
def enregistrer_achat(request, client_id):

    client = get_object_or_404(
        Client,
        id=client_id
    )

    fidelite, _ = Fidelite.objects.get_or_create(
        client=client
    )

    succursale = request.succursale

    if request.method == "POST":

        action = request.POST.get("action")

        try:

            # 1. Achat payant

            if action == "achat_payant":

                achat = enregistrer_achat_payant(
                    client,
                    employe=request.user,
                    succursale=succursale,
                )

                fidelite.refresh_from_db()

                messages.success(
                    request,
                    (
                        f"Achat enregistré dans "
                        f"{succursale.nom}. "
                        f"Étampes : {fidelite.progression}. "
                        f"Récompenses : {fidelite.recompenses}."
                    ),
                )

            # 2. Utilisation d'une recompense

            elif action == "utiliser_recompense":

                achat = utiliser_recompense(
                    client,
                    employe=request.user,
                    succursale=succursale,
                )

                if achat is not None:

                    messages.success(
                        request,
                        (
                            f"Récompense utilisée dans "
                            f"{succursale.nom}."
                        ),
                    )

                else:

                    messages.error(
                        request,
                        "Aucune récompense disponible."
                    )

            # 3. Vente d'une carte prepayee

            elif action == "emettre_carte":

                carte = emettre_carte_prepayee(
                    client,
                    employe=request.user,
                    succursale=succursale,
                )

                messages.success(
                    request,
                    (
                        f"Carte prépayée #{carte.pk} "
                        f"émise dans {succursale.nom}. "
                        f"Solde : {carte.cafes_restants} cafés."
                    ),
                )

            # 4. Consommation prepayee

            elif action == "utiliser_carte":

                carte_id = request.POST.get("carte_id")

                carte = get_object_or_404(
                    CartePrepayee,
                    id=carte_id,
                    client=client,
                )

                achat = utiliser_carte_prepayee(
                    carte,
                    employe=request.user,
                    succursale=succursale,
                )

                if achat is not None:

                    carte.refresh_from_db()

                    messages.success(
                        request,
                        (
                            f"Café consommé dans "
                            f"{succursale.nom}. "
                            f"Solde restant : "
                            f"{carte.cafes_restants} cafés."
                        ),
                    )

                else:

                    messages.error(
                        request,
                        "Cette carte ne peut plus être utilisée."
                    )

            else:

                messages.error(
                    request,
                    "Action inconnue."
                )

        except ValueError as erreur:

            messages.error(
                request,
                str(erreur)
            )

        return redirect(
            "loyalty:enregistrer_achat",
            client_id=client.id,
        )

    cartes_prepayees = (
        CartePrepayee.objects
        .filter(client=client)
        .order_by("-date_emission")
    )

    contexte = {
        "client": client,
        "fidelite": fidelite,
        "cartes_prepayees": cartes_prepayees,
        "succursale": succursale,
    }

    return render(
        request,
        "loyalty/enregistrer_achat.html",
        contexte,
    )
@gerant_required
def rapport_statistiques(request):
    """
    Le gerant consulte uniquement sa succursale.

    Le proprietaire peut consulter une succursale
    ou l'ensemble du reseau.
    """

    proprietaire = est_proprietaire(request.user)

    # 1. Determiner les succursales accessibles

    if proprietaire:

        succursales = Succursale.objects.all()

        succursale_gerant = None

    else:

        succursales = obtenir_succursales_autorisees(
            request.user
        )

        succursale_gerant = succursales.first()

        if succursale_gerant is None:

            raise PermissionDenied(
                "Aucune succursale autorisee."
            )

    # 2. Construire le formulaire

    formulaire = RapportStatistiquesForm(
        request.GET or None,
        succursales=succursales,
        est_proprietaire=proprietaire,
    )

    rapport = None

    # 3. Generer le rapport

    if formulaire.is_valid():

        date_debut = formulaire.cleaned_data[
            "date_debut"
        ]

        date_fin = formulaire.cleaned_data[
            "date_fin"
        ]

        if proprietaire:

            succursale = formulaire.cleaned_data[
                "succursale"
            ]

        else:

            succursale = succursale_gerant

        rapport = generer_rapport(
            date_debut,
            date_fin,
            succursale=succursale,
        )

    # 4. Afficher le resultat

    return render(
        request,
        "loyalty/rapport_statistiques.html",
        {
            "formulaire": formulaire,
            "rapport": rapport,
            "est_proprietaire": proprietaire,
            "succursale_gerant": succursale_gerant,
        },
    )

@proprietaire_required
def fusion_clients(request):
    """
    Interface de fusion reservee au proprietaire.
    """

    if request.method == "POST":

        form = FusionClientForm(request.POST)

        if form.is_valid():

            principal = form.cleaned_data[
                "client_principal"
            ]

            secondaire = form.cleaned_data[
                "client_secondaire"
            ]

            try:

                fusion = fusionner_clients(
                    client_principal_id=principal.pk,
                    client_secondaire_id=secondaire.pk,
                    gerant=request.user,
                )

            except (ValueError, PermissionError) as erreur:

                form.add_error(None, str(erreur))

            else:

                messages.success(
                    request,
                    (
                        "Fusion effectuee avec succes. "
                        f"Reference : #{fusion.pk}."
                    ),
                )

                return redirect(
                    "loyalty:fusion_clients"
                )

    else:

        form = FusionClientForm()

    return render(
        request,
        "loyalty/fusion_clients.html",
        {
            "form": form,
        },
    )


@proprietaire_required
def anonymisation_client(request):
    """
    Interface d'anonymisation reservee au proprietaire.
    """

    if request.method == "POST":

        form = AnonymisationClientForm(request.POST)

        if form.is_valid():

            client = form.cleaned_data["client"]

            try:

                anonymiser_client(
                    client_id=client.pk,
                    gerant=request.user,
                )

            except (ValueError, PermissionError) as erreur:

                form.add_error(None, str(erreur))

            else:

                messages.success(
                    request,
                    "Le client a ete anonymise avec succes.",
                )

                return redirect(
                    "loyalty:anonymisation_client"
                )

    else:

        form = AnonymisationClientForm()

    return render(
        request,
        "loyalty/anonymisation_client.html",
        {
            "form": form,
        },
    )


@gerant_required
def journal_audit(request):
    """
    Affiche le journal des operations sensibles.

    Le gerant consulte uniquement les operations
    de sa succursale.

    Le proprietaire consulte toutes les operations
    du reseau.
    """

    # 1. Recuperer les journaux

    journaux = JournalAudit.objects.select_related(
        "utilisateur",
        "succursale",
    )

    # 2. Filtrer selon les permissions

    if not est_proprietaire(request.user):

        succursales = obtenir_succursales_autorisees(
            request.user
        )

        journaux = journaux.filter(
        succursale__in=succursales
        ).exclude(
        action__in=[
            JournalAudit.TypeAction.FUSION,
            JournalAudit.TypeAction.ANONYMISATION,
            JournalAudit.TypeAction.REGLE_FIDELITE,
        ])

    # 3. Recuperer les 100 dernieres operations

    journaux = journaux.order_by(
        "-date_action",
        "-pk",
    )[:100]

    # 4. Afficher le journal

    return render(
        request,
        "loyalty/journal_audit.html",
        {
            "journaux": journaux,
        },
    )


@gerant_required
def annuler_transaction(request):
    """
    Permet au gerant d'annuler une transaction
    de sa succursale.

    Le proprietaire peut acceder aux transactions
    de toutes les succursales.
    """

    # 1. Recuperer les transactions

    achats = Achat.objects.select_related(
        "client",
        "employe",
        "succursale",
    )

    emissions = EmissionCarte.objects.select_related(
        "carte__client",
        "succursale",
    )

    # 2. Filtrer selon les permissions

    if not est_proprietaire(request.user):

        succursales = obtenir_succursales_autorisees(
            request.user
        )

        achats = achats.filter(
            succursale__in=succursales
        )

        emissions = emissions.filter(
            succursale__in=succursales
        )

    # 3. Traiter le formulaire

    if request.method == "POST":

        form = AnnulationTransactionForm(request.POST)

        if form.is_valid():

            type_transaction = form.cleaned_data[
                "type_transaction"
            ]

            transaction_id = form.cleaned_data[
                "transaction_id"
            ]

            motif = form.cleaned_data["motif"]

            try:

                # Verifier que la transaction appartient
                # a une succursale autorisee

                if type_transaction == "vente_carte":

                    if not emissions.filter(
                        pk=transaction_id
                    ).exists():

                        raise PermissionDenied(
                            "Transaction inexistante ou non autorisee."
                        )

                else:

                    if not achats.filter(
                        pk=transaction_id
                    ).exists():

                        raise PermissionDenied(
                            "Transaction inexistante ou non autorisee."
                        )

                # Annulation d'un achat payant

                if type_transaction == "payant":

                    annuler_achat_payant(
                        achat_id=transaction_id,
                        gerant=request.user,
                        motif=motif,
                    )

                # Annulation d'un cafe gratuit

                elif type_transaction == "gratuit":

                    annuler_utilisation_recompense(
                        achat_id=transaction_id,
                        gerant=request.user,
                        motif=motif,
                    )

                # Annulation d'un cafe prepaye

                elif type_transaction == "prepaye":

                    annuler_utilisation_carte(
                        achat_id=transaction_id,
                        gerant=request.user,
                        motif=motif,
                    )

                # Annulation d'une vente de carte

                elif type_transaction == "vente_carte":

                    annuler_vente_carte(
                        emission_id=transaction_id,
                        gerant=request.user,
                        motif=motif,
                    )

            except (
                Achat.DoesNotExist,
                EmissionCarte.DoesNotExist,
            ):

                form.add_error(
                    "transaction_id",
                    "Transaction introuvable.",
                )

            except (ValueError, PermissionError) as erreur:

                form.add_error(None, str(erreur))

            else:

                messages.success(
                    request,
                    "Transaction annulee avec succes.",
                )

                return redirect(
                    "loyalty:annuler_transaction"
                )

    else:

        form = AnnulationTransactionForm()

    # 4. Recuperer les 20 derniers achats autorises

    achats_recents = achats.order_by("-pk")[:20]

    # 5. Recuperer les 20 dernieres ventes autorisees

    ventes_cartes = emissions.order_by("-pk")[:20]

    # 6. Afficher la page

    return render(
        request,
        "loyalty/annuler_transaction.html",
        {
            "form": form,
            "achats_recents": achats_recents,
            "ventes_cartes": ventes_cartes,
        },
    )
