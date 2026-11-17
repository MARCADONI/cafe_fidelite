from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404

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
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        est_employe = (
            request.user.is_superuser
            or request.user.groups.filter(
                name__in=["Barista", "Gerant"]
            ).exists()
        )

        if not est_employe:
            raise PermissionDenied(
                "Accès réservé aux employés du café."
            )

        return view_func(request, *args, **kwargs)

    return wrapper

def gerant_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        est_gerant = (
            request.user.is_superuser
            or request.user.groups.filter(name="Gerant").exists()
        )

        if not est_gerant:
            raise PermissionDenied(
                "Cette fonctionnalité est réservée au gérant."
            )

        return view_func(request, *args, **kwargs)

    return wrapper

@employe_required
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

@employe_required
def enregistrer_achat(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    fidelite, _ = Fidelite.objects.get_or_create(client=client)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "achat_payant":
            

            achat = enregistrer_achat_payant(client,employe=request.user)
            fidelite.refresh_from_db()

            messages.success(
                request,
                (
                    f"L'achat de {client.nom} a été enregistré. "
                    f"Progression : {fidelite.progression}/10. "
                    f"Récompenses disponibles : {fidelite.recompenses}."
                ),
            )

        elif action == "utiliser_recompense":
            
            achat = utiliser_recompense(client,employe=request.user)

            if achat is not None:
                messages.success(
                    request,
                    f"La récompense de {client.nom} a été utilisée avec succès.",
                )
            else:
                messages.error(
                    request,
                    "Aucune récompense disponible pour ce client.",
        
               )

        elif action == "emettre_carte":
            carte = emettre_carte_prepayee(client,employe=request.user)

            messages.success(
                request,
                (
                    f"Une carte prépayée de 11 cafés a été émise "
                    f"pour {client.nom}."
                ),
            )
        elif action == "utiliser_carte":
            carte_id = request.POST.get("carte_id")

            carte = get_object_or_404(
                CartePrepayee,
                id=carte_id,
                client=client,
            )

            achat = utiliser_carte_prepayee(carte, employe=request.user)

            if achat is not None:
                messages.success(
                    request,
                    (
                        f"Un café a été utilisé sur la carte #{carte.id}. "
                        f"Il reste {carte.cafes_restants} café(s)."
                    ),
                )
            else:
                messages.error(
                    request,
                    "Cette carte ne peut plus être utilisée.",
                )
                
        return redirect(
            "loyalty:enregistrer_achat",
            client_id=client.id,
        )

    cartes_prepayees = CartePrepayee.objects.filter(
    client=client,
    ).order_by("-date_emission")

    contexte = {
        "client": client,
        "fidelite": fidelite,
        "cartes_prepayees": cartes_prepayees,
    }

    return render(
        request,
        "loyalty/enregistrer_achat.html",
        contexte,
    )




@gerant_required
def rapport_statistiques(request):
    """
    Affiche les statistiques du cafe.
    Acces reserve au gerant.
    """
    formulaire = RapportStatistiquesForm(
        request.GET or None
    )

    rapport = None

    if formulaire.is_valid():
        rapport = generer_rapport(
            formulaire.cleaned_data["date_debut"],
            formulaire.cleaned_data["date_fin"],
        )

    return render(
        request,
        "loyalty/rapport_statistiques.html",
        {
            "formulaire": formulaire,
            "rapport": rapport,
        },
    )



@gerant_required
def fusion_clients(request):
    """
    Interface de fusion reservee au gerant.
    """
    # 2. Traiter le formulaire
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
                form.add_error(
                    None,
                    str(erreur),
                )

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

    # 3. Afficher le formulaire
    return render(
        request,
        "loyalty/fusion_clients.html",
        {
            "form": form,
        },
    )




@gerant_required
def anonymisation_client(request):
    """
    Interface d'anonymisation reservee au gerant.
    """


    # 2. Traiter le formulaire
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

    # 3. Afficher la page
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
    Accessible uniquement aux gerants.
    """

    journaux = (
        JournalAudit.objects
        .select_related("utilisateur")
        .order_by("-date_action")[:100]
    )

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
    Permet au gerant d'annuler une transaction.

    Types acceptes :
    - Achat payant
    - Cafe gratuit
    - Cafe prepaye
    - Vente de carte prepayee
    """

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

            except (Achat.DoesNotExist, EmissionCarte.DoesNotExist):
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

        # Recuperer les 20 derniers achats
    achats_recents = (
        Achat.objects
        .select_related("client", "employe")
        .order_by("-pk")[:20]
    )
    # Recuperer les 20 dernieres ventes de cartes
    ventes_cartes = (
        EmissionCarte.objects
        .select_related("carte__client")
        .order_by("-pk")[:20]
    )

    return render(
    request,
    "loyalty/annuler_transaction.html",
    {
        "form": form,
        "achats_recents": achats_recents,
        "ventes_cartes": ventes_cartes,
    },
    )
