from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import ClientForm
from .models import CartePrepayee, Client, Fidelite
from .services import (
    emettre_carte_prepayee,
    enregistrer_achat_payant,
    utiliser_carte_prepayee,
    utiliser_recompense,
)

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

