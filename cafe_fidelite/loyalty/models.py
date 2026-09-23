from django.db import models


class Client(models.Model):
    nom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, unique=True)
    courriel = models.EmailField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.telephone}"

class Fidelite(models.Model):
    client = models.OneToOneField(
        Client,
        on_delete=models.CASCADE,
        related_name="fidelite",
    )
    progression = models.PositiveIntegerField(default=0)
    recompenses = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Fidelite de {self.client.nom}"

class CartePrepayee(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="cartes_prepayees",
    )
    cafes_restants = models.PositiveIntegerField(default=11)
    date_emission = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

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

    def __str__(self):
        return f"{self.client.nom} - {self.get_type_achat_display()}"