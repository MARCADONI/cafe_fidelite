from django import forms

from .models import Client


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
