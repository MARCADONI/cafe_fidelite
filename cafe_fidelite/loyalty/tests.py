

# =====================================================
# IMPORTS PYTHON
# =====================================================

from datetime import date, datetime, timedelta, timezone as dt_timezone


# =====================================================
# IMPORTS DJANGO
# =====================================================

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


# =====================================================
# MODELES DE L'APPLICATION
# =====================================================

from cafe_fidelite.loyalty.models import (
    Client,
    Fidelite,
    Achat,
    Annulation,
    MouvementFidelite,
    CartePrepayee,
    EmissionCarte,
    RegleFidelite,
)


# =====================================================
# SERVICES DE L'APPLICATION
# =====================================================

from cafe_fidelite.loyalty.services import (
    obtenir_regle_fidelite,
    enregistrer_achat_payant,
    annuler_achat_payant,
    utiliser_recompense,
    annuler_utilisation_recompense,
    emettre_carte_prepayee,
    utiliser_carte_prepayee,
    annuler_utilisation_carte,
    annuler_vente_carte,
)


# =====================================================
# RAPPORTS STATISTIQUES
# =====================================================

from cafe_fidelite.loyalty.rapports import (
    generer_rapport,
)


class RegleFideliteTests(TestCase):

    def setUp(self):
        RegleFidelite.objects.create(
            seuil=10,
            date_entree_vigueur=(
                timezone.now() - timedelta(days=30)
            ),
        )

    def test_regle_actuelle(self):
        regle = obtenir_regle_fidelite()
        self.assertEqual(regle.seuil, 10)

    def test_regle_future_non_appliquee(self):
        RegleFidelite.objects.create(
            seuil=12,
            date_entree_vigueur=(
                timezone.now() + timedelta(days=10)
            ),
        )

        regle = obtenir_regle_fidelite()
        self.assertEqual(regle.seuil, 10)

    def test_regle_future_apres_entree_en_vigueur(self):
        date_future = (
            timezone.now() + timedelta(days=10)
        )

        RegleFidelite.objects.create(
            seuil=12,
            date_entree_vigueur=date_future,
        )

        regle = obtenir_regle_fidelite(
            date_future + timedelta(minutes=1)
        )

        self.assertEqual(regle.seuil, 12)


class AnnulationAchatPayantTests(TestCase):

    def setUp(self):
        User = get_user_model()

        groupe_gerant, _ = Group.objects.get_or_create(
            name="gerant"
        )

        self.gerant = User.objects.create_user(
            username="gerant_test",
            password="mot_de_passe_test",
        )

        self.gerant.groups.add(groupe_gerant)

        self.client = Client.objects.create(
            nom="Client Test",
            telephone="5551234567",
        )

        self.fidelite = Fidelite.objects.create(
            client=self.client,
            progression=5,
            recompenses=0,
        )

    def test_annulation_achat_simple(self):
        achat = enregistrer_achat_payant(
            self.client,
            employe=self.gerant,
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            6,
        )

        annuler_achat_payant(
            achat.id,
            self.gerant,
            "Erreur de saisie",
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            5,
        )

        self.assertTrue(
            Annulation.objects.filter(
                achat=achat
            ).exists()
        )

    def test_annulation_avec_recompense_disponible(self):
        self.fidelite.progression = 9
        self.fidelite.recompenses = 0
        self.fidelite.save()

        achat = enregistrer_achat_payant(
            self.client,
            employe=self.gerant,
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            0
        )

        self.assertEqual(
            self.fidelite.recompenses,
            1
        )

        annuler_achat_payant(
            achat.id,
            self.gerant,
            "Achat enregistre par erreur",
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            9
        )

        self.assertEqual(
            self.fidelite.recompenses,
            0
        )

        self.assertEqual(
            self.fidelite.dette_etampes,
            0
        )
    
    
    def test_mouvements_achat_avec_recompense(self):
        self.fidelite.progression = 9
        self.fidelite.recompenses = 0
        self.fidelite.dette_etampes = 0
        self.fidelite.save()

        achat = enregistrer_achat_payant(
            self.client,
            employe=self.gerant,
        )

        mouvements = list(
            achat.mouvements_fidelite.order_by("id")
        )

        self.assertEqual(len(mouvements), 2)

        total_etampes = sum(
            mouvement.variation_etampes
            for mouvement in mouvements
        )

        total_recompenses = sum(
            mouvement.variation_recompenses
            for mouvement in mouvements
        )

        self.assertEqual(total_etampes, -9)
        self.assertEqual(total_recompenses, 1)

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            0
        )

        self.assertEqual(
            self.fidelite.recompenses,
            1
        )


    
    def test_annulation_cree_mouvement_compensatoire(self):
        self.fidelite.progression = 5
        self.fidelite.recompenses = 0
        self.fidelite.dette_etampes = 0
        self.fidelite.save()

        achat = enregistrer_achat_payant(
            self.client,
            employe=self.gerant,
        )

        annulation = annuler_achat_payant(
            achat.id,
            self.gerant,
            "Erreur de saisie",
        )

        mouvement = MouvementFidelite.objects.get(
            annulation=annulation
        )

        self.assertEqual(
            mouvement.variation_etampes,
            -1,
        )

        self.assertEqual(
            mouvement.variation_dette,
            0,
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.progression,
            5,
        )


    
    def test_impossible_annuler_deux_fois(self):
        achat = enregistrer_achat_payant(
            self.client,
            employe=self.gerant,
        )

        annuler_achat_payant(
            achat.id,
            self.gerant,
            "Premiere annulation",
        )

        with self.assertRaises(ValueError):
            annuler_achat_payant(
                achat.id,
                self.gerant,
                "Deuxieme annulation",
            )




class UtilisationRecompenseTests(TestCase):

    def setUp(self):
        User = get_user_model()

        groupe_gerant, _ = Group.objects.get_or_create(
            name="gerant"
        )

        self.gerant = User.objects.create_user(
            username="gerant_recompense_test",
            password="test12345",
        )

        self.gerant.groups.add(groupe_gerant)

        self.client = Client.objects.create(
            nom="Client Recompense",
            telephone="5559876543",
        )

        self.fidelite = Fidelite.objects.create(
            client=self.client,
            progression=0,
            recompenses=2,
        )

    def test_utilisation_recompense(self):
        achat = utiliser_recompense(
            self.client,
            employe=self.gerant,
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.recompenses,
            1,
        )

        self.assertEqual(
            achat.type_achat,
            Achat.TypeAchat.GRATUIT_FIDELITE,
        )

        mouvement = MouvementFidelite.objects.get(
            achat=achat,
            type_mouvement=(
                MouvementFidelite.TypeMouvement.UTILISATION
            ),
        )

        self.assertEqual(
            mouvement.variation_recompenses,
            -1,
        )

    def test_annulation_restitue_recompense(self):
        achat = utiliser_recompense(
            self.client,
            employe=self.gerant,
        )

        annulation = annuler_utilisation_recompense(
            achat.id,
            self.gerant,
            "Erreur de saisie",
        )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.recompenses,
            2,
        )

        self.assertTrue(
            Annulation.objects.filter(
                pk=annulation.pk,
                achat=achat,
            ).exists()
        )

        mouvement = MouvementFidelite.objects.get(
            annulation=annulation
        )

        self.assertEqual(
            mouvement.variation_recompenses,
            1,
        )

    def test_impossible_utiliser_sans_recompense(self):
        self.fidelite.recompenses = 0
        self.fidelite.save()

        with self.assertRaises(ValueError):
            utiliser_recompense(
                self.client,
                employe=self.gerant,
            )

    def test_impossible_annuler_deux_fois(self):
        achat = utiliser_recompense(
            self.client,
            employe=self.gerant,
        )

        annuler_utilisation_recompense(
            achat.id,
            self.gerant,
            "Premiere annulation",
        )

        with self.assertRaises(ValueError):
            annuler_utilisation_recompense(
                achat.id,
                self.gerant,
                "Deuxieme annulation",
            )

        self.fidelite.refresh_from_db()

        self.assertEqual(
            self.fidelite.recompenses,
            2,
        )



class CartePrepayeeTests(TestCase):

    def setUp(self):
        User = get_user_model()

        groupe_gerant, _ = Group.objects.get_or_create(
            name="gerant"
        )

        self.gerant = User.objects.create_user(
            username="gerant_carte_test",
            password="test12345",
        )

        self.gerant.groups.add(groupe_gerant)

        self.client = Client.objects.create(
            nom="Client Carte",
            telephone="5552223333",
        )

    def test_emission_carte(self):
        carte = emettre_carte_prepayee(
            self.client,
            employe=self.gerant,
        )

        self.assertEqual(
            carte.cafes_restants,
            11,
        )

        self.assertTrue(
            EmissionCarte.objects.filter(
                carte=carte
            ).exists()
        )

    def test_utilisation_carte(self):
        carte = emettre_carte_prepayee(
            self.client,
            employe=self.gerant,
        )

        achat = utiliser_carte_prepayee(
            carte,
            employe=self.gerant,
        )

        carte.refresh_from_db()

        self.assertEqual(
            carte.cafes_restants,
            10,
        )

        self.assertEqual(
            achat.type_achat,
            Achat.TypeAchat.PREPAYE,
        )

    def test_annulation_utilisation(self):
        carte = emettre_carte_prepayee(
            self.client,
            employe=self.gerant,
        )

        achat = utiliser_carte_prepayee(
            carte,
            employe=self.gerant,
        )

        annulation = annuler_utilisation_carte(
            achat.id,
            self.gerant,
            "Erreur de saisie",
        )

        carte.refresh_from_db()

        self.assertEqual(
            carte.cafes_restants,
            11,
        )

        self.assertTrue(
            Annulation.objects.filter(
                pk=annulation.pk
            ).exists()
        )

    def test_annulation_vente_carte(self):
        carte = emettre_carte_prepayee(
            self.client,
            employe=self.gerant,
        )

        annuler_vente_carte(
            carte.emission.id,
            self.gerant,
            "Vente enregistree par erreur",
        )

        carte.refresh_from_db()

        self.assertTrue(carte.est_annulee)
        self.assertFalse(carte.active)

    def test_impossible_annuler_vente_utilisee(self):
        carte = emettre_carte_prepayee(
            self.client,
            employe=self.gerant,
        )

        utiliser_carte_prepayee(
            carte,
            employe=self.gerant,
        )

        with self.assertRaises(ValueError):
            annuler_vente_carte(
                carte.emission.id,
                self.gerant,
                "Annulation impossible",
            )



class RapportStatistiquesTests(TestCase):

    def setUp(self):
        User = get_user_model()

        groupe, _ = Group.objects.get_or_create(
            name="gerant"
        )

        self.gerant = User.objects.create_user(
            username="gerant_rapport",
            password="test12345",
        )
        self.gerant.groups.add(groupe)

        self.barista = User.objects.create_user(
            username="barista_rapport",
            password="test12345",
        )

        self.client_cafe = Client.objects.create(
            nom="Client Rapport",
            telephone="5551112222",
        )

    def test_rapport_exclut_achat_annule(self):
        achat_valide = Achat.objects.create(
            client=self.client_cafe,
            type_achat=Achat.TypeAchat.PAYANT,
        )

        achat_annule = Achat.objects.create(
            client=self.client_cafe,
            type_achat=Achat.TypeAchat.PAYANT,
        )

        Annulation.objects.create(
            achat=achat_annule,
            gerant=self.gerant,
            motif="Erreur",
        )

        aujourd_hui = timezone.localdate()

        rapport = generer_rapport(
            aujourd_hui,
            aujourd_hui,
        )

        self.assertEqual(
            rapport["cafes_payants"],
            1,
        )

    def test_rapport_compte_cartes(self):
        carte = CartePrepayee.objects.create(
            client=self.client_cafe,
            cafes_restants=11,
        )

        EmissionCarte.objects.create(
            carte=carte,
            employe=self.gerant,
            date_emission=timezone.now(),
        )

        aujourd_hui = timezone.localdate()

        rapport = generer_rapport(
            aujourd_hui,
            aujourd_hui,
        )

        self.assertEqual(
            rapport["cartes_vendues"],
            1,
        )

    def test_barista_ne_peut_pas_voir_rapport(self):
        self.client.force_login(self.barista)

        reponse = self.client.get(
            reverse("loyalty:rapport_statistiques")
        )

        self.assertEqual(
            reponse.status_code,
            403,
        )

    def test_gerant_peut_voir_rapport(self):
        self.client.force_login(self.gerant)

        reponse = self.client.get(
            reverse("loyalty:rapport_statistiques"),
            {
                "date_debut": "2026-10-01",
                "date_fin": "2026-10-18",
            },
        )

        self.assertEqual(
            reponse.status_code,
            200,
        )

        self.assertIn(
            "rapport",
            reponse.context,
        )
