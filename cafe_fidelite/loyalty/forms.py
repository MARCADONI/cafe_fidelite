from django import forms

from .models import Client

from django.core.exceptions import ValidationError
from cafe_fidelite.loyalty.models import Client


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
