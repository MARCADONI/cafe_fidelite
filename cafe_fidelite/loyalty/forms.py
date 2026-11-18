from django import forms

from .models import Client

from django.core.exceptions import ValidationError
from cafe_fidelite.loyalty.models import Client
from .models import Succursale


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("nom", "telephone", "courriel")



class RapportStatistiquesForm(forms.Form):

    date_debut = forms.DateField(
        label="Date de debut",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )

    date_fin = forms.DateField(
        label="Date de fin",
        widget=forms.DateInput(
            attrs={"type": "date"},
            format="%Y-%m-%d",
        ),
        input_formats=["%Y-%m-%d"],
    )

    succursale = forms.ModelChoiceField(
        queryset=Succursale.objects.none(),
        label="Succursale",
        required=False,
        empty_label="Toutes les succursales",
    )

    def __init__(
        self,
        *args,
        succursales=None,
        est_proprietaire=False,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        if succursales is not None:

            self.fields["succursale"].queryset = (
                succursales.order_by("nom")
            )

        # Le gerant ne choisit pas sa succursale

        if not est_proprietaire:

            self.fields.pop("succursale")

    def clean(self):

        donnees = super().clean()

        debut = donnees.get("date_debut")
        fin = donnees.get("date_fin")

        if debut and fin and debut > fin:

            raise forms.ValidationError(
                "La date de debut doit etre "
                "anterieure ou egale a la date de fin."
            )

        return donnees

class FusionClientForm(forms.Form):

    client_principal = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        label="Client principal (a conserver)",
        empty_label="Selectionner le client principal",
    )

    client_secondaire = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        label="Client secondaire (a fusionner)",
        empty_label="Selectionner le client secondaire",
    )

    confirmation = forms.BooleanField(
        label=(
            "Je confirme vouloir fusionner ces "
            "deux comptes clients."
        ),
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        clients_actifs = (
            Client.objects.filter(
                est_fusionne=False,
                est_anonymise=False,
            )
            .order_by("nom", "pk")
        )

        self.fields[
            "client_principal"
        ].queryset = clients_actifs

        self.fields[
            "client_secondaire"
        ].queryset = clients_actifs

    def clean(self):
        cleaned_data = super().clean()

        principal = cleaned_data.get(
            "client_principal"
        )

        secondaire = cleaned_data.get(
            "client_secondaire"
        )

        if (
            principal is not None
            and secondaire is not None
            and principal.pk == secondaire.pk
        ):
            raise ValidationError(
                "Vous devez selectionner "
                "deux clients differents."
            )

        return cleaned_data



class AnonymisationClientForm(forms.Form):
    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        label="Client a anonymiser",
        empty_label="Selectionner un client",
    )

    confirmation = forms.BooleanField(
        label="Je confirme l'anonymisation du client",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["client"].queryset = (
            Client.objects.filter(
                est_anonymise=False,
                est_fusionne=False,
            )
            .order_by("nom", "pk")
        )


class AnnulationTransactionForm(forms.Form):

    TYPES_TRANSACTION = [
        ("payant", "Achat payant"),
        ("gratuit", "Cafe gratuit"),
        ("prepaye", "Cafe prepaye"),
        ("vente_carte", "Vente d'une carte prepayee"),
    ]

    type_transaction = forms.ChoiceField(
        choices=TYPES_TRANSACTION,
        label="Type de transaction",
    )

    transaction_id = forms.IntegerField(
        min_value=1,
        label="Identifiant de la transaction",
    )

    motif = forms.CharField(
        max_length=500,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": (
                    "Expliquez pourquoi la transaction "
                    "doit etre annulee."
                ),
            }
        ),
        label="Motif de l'annulation",
    )
