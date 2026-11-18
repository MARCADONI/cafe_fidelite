from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Achat,
    CartePrepayee,
    Client,
    Fidelite,
    Succursale,
    AffectationSuccursale,
    RegleFidelite,
)

from .services_succursales import est_proprietaire

from .services import programmer_regle_fidelite


# =====================================================
# PERMISSIONS COMMUNES
# =====================================================

class ProprietaireAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return est_proprietaire(request.user)

    def has_view_permission(self, request, obj=None):
        return est_proprietaire(request.user)

    def has_add_permission(self, request):
        return est_proprietaire(request.user)

    def has_change_permission(self, request, obj=None):
        return est_proprietaire(request.user)

    def has_delete_permission(self, request, obj=None):
        return False


# =====================================================
# ADMINISTRATION EN LECTURE SEULE
# =====================================================

class LectureSeuleAdmin(ProprietaireAdmin):

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# =====================================================
# CLIENTS
# =====================================================

@admin.register(Client)
class ClientAdmin(LectureSeuleAdmin):

    list_display = (
        "nom",
        "telephone",
        "courriel",
        "date_creation",
        "est_anonymise",
        "est_fusionne",
    )

    search_fields = (
        "nom",
        "telephone",
        "courriel",
    )


# =====================================================
# FIDELITE
# =====================================================

@admin.register(Fidelite)
class FideliteAdmin(LectureSeuleAdmin):

    list_display = (
        "client",
        "progression",
        "recompenses",
        "dette_etampes",
    )

    search_fields = (
        "client__nom",
        "client__telephone",
    )


# =====================================================
# CARTES PREPAYEES
# =====================================================

@admin.register(CartePrepayee)
class CartePrepayeeAdmin(LectureSeuleAdmin):

    list_display = (
        "client",
        "cafes_restants",
        "date_emission",
        "active",
    )

    search_fields = (
        "client__nom",
        "client__telephone",
    )

    list_filter = ("active",)


# =====================================================
# ACHATS
# =====================================================

@admin.register(Achat)
class AchatAdmin(LectureSeuleAdmin):

    list_display = (
        "client",
        "type_achat",
        "succursale",
        "employe",
        "carte_prepayee",
        "date_achat",
    )

    search_fields = (
        "client__nom",
        "client__telephone",
    )

    list_filter = (
        "type_achat",
        "succursale",
    )


# =====================================================
# SUCCURSALES
# =====================================================

@admin.register(Succursale)
class SuccursaleAdmin(ProprietaireAdmin):

    list_display = (
        "code",
        "nom",
        "adresse",
        "active",
        "date_creation",
    )

    search_fields = (
        "code",
        "nom",
        "adresse",
    )

    list_filter = ("active",)

    readonly_fields = ("date_creation",)


# =====================================================
# FORMULAIRE DES AFFECTATIONS
# =====================================================

class AffectationSuccursaleAdminForm(forms.ModelForm):

    class Meta:
        model = AffectationSuccursale
        fields = "__all__"

    def clean(self):

        donnees = super().clean()

        employe = donnees.get("employe")
        succursale = donnees.get("succursale")
        active = donnees.get("active")

        if employe is None or succursale is None:
            return donnees

        # Verifier le role de l'employe

        if not employe.groups.filter(
            name__in=["Barista", "Gerant"]
        ).exists():

            self.add_error(
                "employe",
                "Selectionnez un barista ou un gerant.",
            )

        # Une affectation active necessite
        # une succursale active

        if active and not succursale.active:

            self.add_error(
                "succursale",
                "Cette succursale est inactive.",
            )

        if active and not employe.is_active:

            self.add_error(
                "employe",
                "Cet employe est inactif.",
            )

        # Un gerant ne peut avoir qu'une seule
        # affectation active

        if active and employe.groups.filter(
            name="Gerant"
        ).exists():

            affectations = (
                AffectationSuccursale.objects.filter(
                    employe=employe,
                    active=True,
                )
            )

            if self.instance.pk:

                affectations = affectations.exclude(
                    pk=self.instance.pk
                )

            if affectations.exists():

                self.add_error(
                    "succursale",
                    "Un gerant ne peut avoir qu'une "
                    "seule affectation active.",
                )

        return donnees


# =====================================================
# AFFECTATIONS DES EMPLOYES
# =====================================================

@admin.register(AffectationSuccursale)
class AffectationSuccursaleAdmin(ProprietaireAdmin):

    form = AffectationSuccursaleAdminForm

    list_display = (
        "employe",
        "succursale",
        "active",
        "date_affectation",
    )

    list_filter = (
        "succursale",
        "active",
    )

    search_fields = (
        "employe__username",
        "succursale__nom",
        "succursale__code",
    )

    readonly_fields = ("date_affectation",)

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs,
    ):

        if db_field.name == "employe":

            User = get_user_model()

            kwargs["queryset"] = (
                User.objects.filter(
                    groups__name__in=[
                        "Barista",
                        "Gerant",
                    ]
                ).distinct()
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )


# =====================================================
# FORMULAIRE DES REGLES DE FIDELITE
# =====================================================

class RegleFideliteAdminForm(forms.ModelForm):

    class Meta:
        model = RegleFidelite

        fields = (
            "seuil",
            "date_entree_vigueur",
        )

    def clean_date_entree_vigueur(self):

        date = self.cleaned_data[
            "date_entree_vigueur"
        ]

        if date <= timezone.now():

            raise forms.ValidationError(
                "La date d'entree en vigueur "
                "doit etre future."
            )

        return date


# =====================================================
# REGLES DE FIDELITE
# =====================================================

@admin.register(RegleFidelite)
class RegleFideliteAdmin(ProprietaireAdmin):

    form = RegleFideliteAdminForm

    fields = (
        "seuil",
        "date_entree_vigueur",
    )

    list_display = (
        "seuil",
        "date_entree_vigueur",
        "date_creation",
        "cree_par",
    )

    ordering = ("-date_entree_vigueur",)

    def has_change_permission(self, request, obj=None):

        return False

    def save_model(self, request, obj, form, change):

        regle = programmer_regle_fidelite(
            seuil=obj.seuil,
            date_entree_vigueur=obj.date_entree_vigueur,
            gerant=request.user,
        )

        obj.pk = regle.pk
        obj.cree_par = regle.cree_par
        obj.date_creation = regle.date_creation

        obj._state.adding = False
        obj._state.db = regle._state.db