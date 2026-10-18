from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Client(models.Model):
    nom = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )

    telephone = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    courriel = models.EmailField(
        blank=True,
        default=""
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    est_anonymise = models.BooleanField(
        default=False
    )

    date_anonymisation = models.DateTimeField(
        null=True,
        blank=True
    )

    est_fusionne = models.BooleanField(
        default=False
    )

    fusionne_vers = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anciens_doublons"
    )

    def __str__(self):
        if self.est_anonymise:
            return f"Client anonymise #{self.id}"

        if self.est_fusionne:
            return f"Client fusionne #{self.id}"

        return self.nom


class Fidelite(models.Model):
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name="fidelite"
    )

    progression = models.PositiveIntegerField(
        default=0
    )

    recompenses = models.PositiveIntegerField(
        default=0
    )

    dette_etampes = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return (
            f"Fidelite du client #{self.client_id} - "
            f"{self.progression} etampes, "
            f"{self.recompenses} recompenses, "
            f"{self.dette_etampes} etampes de dette"
        )


class CartePrepayee(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="cartes_prepayees",
    )
    cafes_restants = models.PositiveIntegerField(default=11)
    date_emission = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    
    est_annulee = models.BooleanField(
        default=False
    )

    est_cloturee = models.BooleanField(
        default=False
    )


    def __str__(self):
        return f"Carte de {self.client.nom} - {self.cafes_restants} cafes restants"

class Achat(models.Model):
    class TypeAchat(models.TextChoices):
        PAYANT = "PAYANT", "Payant"
        GRATUIT_FIDELITE = "GRATUIT_FIDELITE", "Gratuit - fidelite"
        PREPAYE = "PREPAYE", "Prepayé"

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="achats",
    )
    type_achat = models.CharField(
        max_length=20,
        choices=TypeAchat.choices,
        default=TypeAchat.PAYANT,
    )
    carte_prepayee = models.ForeignKey(
        CartePrepayee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="achats",
    )
    date_achat = models.DateTimeField(auto_now_add=True)

    employe = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="achats_enregistres"
    )

    seuil_fidelite_applique = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    etampes_ajoutees = models.PositiveIntegerField(
        default=0
    )

    dette_remboursee = models.PositiveIntegerField(
        default=0
    )

    recompenses_generees = models.PositiveIntegerField(
        default=0
    )

    
    effets_traces = models.BooleanField(
        default=False
    )


    def __str__(self):
        return f"{self.client.nom} - {self.get_type_achat_display()}"



class RegleFidelite(models.Model):
    seuil = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    date_entree_vigueur = models.DateTimeField(
        unique=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="regles_fidelite_creees"
    )

    class Meta:
        ordering = ["date_entree_vigueur"]

    def __str__(self):
        return (
            f"{self.seuil} etampes "
            f"a partir du {self.date_entree_vigueur}"
        )



class EmissionCarte(models.Model):
    carte = models.OneToOneField(
        "CartePrepayee",
        on_delete=models.PROTECT,
        related_name="emission"
    )

    employe = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="emissions_cartes"
    )

    date_emission = models.DateTimeField()

    annulee = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Emission de la carte #{self.carte_id}"




class Annulation(models.Model):
    achat = models.OneToOneField(
        "Achat",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="annulation"
    )

    emission_carte = models.OneToOneField(
        "EmissionCarte",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="annulation"
    )

    gerant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="annulations_effectuees"
    )

    motif = models.TextField()

    date_annulation = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(achat__isnull=False)
                        & models.Q(emission_carte__isnull=True)
                    )
                    |
                    (
                        models.Q(achat__isnull=True)
                        & models.Q(emission_carte__isnull=False)
                    )
                ),
                name="annulation_une_seule_cible"
            )
        ]

    def __str__(self):
        return f"Annulation #{self.pk}"



class FusionClient(models.Model):
    client_principal = models.ForeignKey(
        "Client",
        on_delete=models.PROTECT,
        related_name="fusions_recues"
    )

    client_secondaire = models.ForeignKey(
        "Client",
        on_delete=models.PROTECT,
        related_name="fusions_sources"
    )

    gerant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fusions_effectuees"
    )

    date_fusion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    client_principal=models.F(
                        "client_secondaire"
                    )
                ),
                name="fusion_clients_distincts"
            )
        ]

    def __str__(self):
        return (
            f"Fusion du client #{self.client_secondaire_id} "
            f"vers le client #{self.client_principal_id}"
        )



class MouvementFidelite(models.Model):

    class TypeMouvement(models.TextChoices):
        ACHAT = "ACHAT", "Achat payant"
        CONVERSION = "CONVERSION", "Conversion en recompense"
        UTILISATION = "UTILISATION", "Utilisation recompense"
        ANNULATION = "ANNULATION", "Correction d'annulation"
        FUSION = "FUSION", "Fusion de clients"

    client = models.ForeignKey(
        "Client",
        on_delete=models.PROTECT,
        related_name="mouvements_fidelite",
    )

    achat = models.ForeignKey(
        "Achat",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mouvements_fidelite",
    )

    annulation = models.ForeignKey(
        "Annulation",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="mouvements_fidelite",
    )

    type_mouvement = models.CharField(
        max_length=20,
        choices=TypeMouvement.choices,
    )

    variation_etampes = models.IntegerField(default=0)

    variation_recompenses = models.IntegerField(default=0)

    variation_dette = models.IntegerField(default=0)

    date_mouvement = models.DateTimeField(
        auto_now_add=True
    )

    commentaire = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    def __str__(self):
        return (
            f"Mouvement #{self.pk} - "
            f"{self.type_mouvement}"
        )
