from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import ClientForm
from .models import CartePrepayee, Client, Fidelite,JournalAudit
from .services import (
    emettre_carte_prepayee,
    enregistrer_achat_payant,
    utiliser_carte_prepayee,
    utiliser_recompense,
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

def enregistrer_achat(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    fidelite, _ = Fidelite.objects.get_or_create(client=client)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "achat_payant":
            fidelite = enregistrer_achat_payant(client)

            messages.success(
                request,
                (
                    f"L'achat de {client.nom} a été enregistré. "
                    f"Progression : {fidelite.progression}/10. "
                    f"Récompenses disponibles : {fidelite.recompenses}."
                ),
            )

        elif action == "utiliser_recompense":
            
            achat = utiliser_recompense(client)

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
            carte = emettre_carte_prepayee(client)

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

            achat = utiliser_carte_prepayee(carte)

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




@login_required
def rapport_statistiques(request):
    """
    Affiche les statistiques du cafe.
    Acces reserve au gerant.
    """

    est_gerant = (
        request.user.is_superuser
        or request.user.groups.filter(
            name="gerant"
        ).exists()
    )

    if not est_gerant:
        raise PermissionDenied(
            "Acces reserve au gerant."
        )

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



@login_required
def fusion_clients(request):
    """
    Interface de fusion reservee au gerant.
    """

    # 1. Verifier les permissions
    est_gerant = (
        request.user.is_superuser
        or request.user.groups.filter(
            name="Gerant"
        ).exists()
    )

    if not est_gerant:
        raise PermissionDenied(
            "Acces reserve au gerant."
        )

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




@login_required
def anonymisation_client(request):
    """
    Interface d'anonymisation reservee au gerant.
    """

    # 1. Verifier les permissions
    est_gerant = (
        request.user.is_superuser
        or request.user.groups.filter(
            name="Gerant"
        ).exists()
    )

    if not est_gerant:
        raise PermissionDenied(
            "Acces reserve au gerant."
        )

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



@login_required
def journal_audit(request):
    """
    Affiche le journal des operations sensibles.
    Accessible uniquement aux gerants.
    """

    if not request.user.groups.filter(
        name="Gerant"
    ).exists():
        raise PermissionDenied(
            "Acces reserve au gerant."
        )

    journaux = (
        JournalAudit.objects
        .select_related("utilisateur")
        .all()[:100]
    )

    return render(
        request,
        "loyalty/journal_audit.html",
        {
            "journaux": journaux,
        },
    )
