

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
    FusionClient,
    JournalAudit,
    
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
    fusionner_clients,
    anonymiser_client,
    enregistrer_achat_payant,
    verifier_client_actif,
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



class FusionClientTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_fusion",
            password="Test12345!"
        )

        self.employe = User.objects.create_user(
            username="employe_fusion",
            password="Test12345!"
        )

        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        self.gerant.groups.add(groupe_gerant)

        self.principal = Client.objects.create(
            nom="Alice",
            telephone="1111111111",
            courriel="alice@example.com"
        )

        self.secondaire = Client.objects.create(
            nom="Alice Dupont",
            telephone="2222222222",
            courriel="alice2@example.com"
        )

        self.fidelite_principale = (
            Fidelite.objects.get_or_create(
                client=self.principal
            )[0]
        )

        self.fidelite_secondaire = (
            Fidelite.objects.get_or_create(
                client=self.secondaire
            )[0]
        )

        self.fidelite_principale.progression = 7
        self.fidelite_principale.recompenses = 1
        self.fidelite_principale.dette_etampes = 0
        self.fidelite_principale.save()

        self.fidelite_secondaire.progression = 2
        self.fidelite_secondaire.recompenses = 2
        self.fidelite_secondaire.dette_etampes = 1
        self.fidelite_secondaire.save()

    def test_fusion_additionne_les_soldes(self):
        fusion = fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant
        )

        self.fidelite_principale.refresh_from_db()
        self.fidelite_secondaire.refresh_from_db()
        self.secondaire.refresh_from_db()

        self.assertEqual(
            self.fidelite_principale.progression,
            9
        )

        self.assertEqual(
            self.fidelite_principale.recompenses,
            3
        )

        self.assertEqual(
            self.fidelite_principale.dette_etampes,
            1
        )

        self.assertEqual(
            self.fidelite_secondaire.progression,
            0
        )

        self.assertEqual(
            self.fidelite_secondaire.recompenses,
            0
        )

        self.assertTrue(
            self.secondaire.est_fusionne
        )

        self.assertEqual(
            self.secondaire.fusionne_vers,
            self.principal
        )

        self.assertEqual(
            fusion.gerant,
            self.gerant
        )

    def test_fusion_transfere_les_cartes(self):
        carte = CartePrepayee.objects.create(
            client=self.secondaire,
            cafes_restants=8,
            active=True
        )

        fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant
        )

        carte.refresh_from_db()

        self.assertEqual(
            carte.client,
            self.principal
        )

        self.assertEqual(
            carte.cafes_restants,
            8
        )

    def test_impossible_fusionner_avec_soi_meme(self):
        with self.assertRaises(ValueError):
            fusionner_clients(
                self.principal.id,
                self.principal.id,
                self.gerant
            )

        self.assertEqual(
            FusionClient.objects.count(),
            0
        )

    def test_impossible_fusionner_deux_fois(self):
        fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant
        )

        with self.assertRaises(ValueError):
            fusionner_clients(
                self.principal.id,
                self.secondaire.id,
                self.gerant
            )

        self.assertEqual(
            FusionClient.objects.count(),
            1
        )

    def test_employe_ne_peut_pas_fusionner(self):
        with self.assertRaises(PermissionError):
            fusionner_clients(
                self.principal.id,
                self.secondaire.id,
                self.employe
            )

        self.fidelite_principale.refresh_from_db()

        self.assertEqual(
            self.fidelite_principale.progression,
            7
        )

        self.assertEqual(
            FusionClient.objects.count(),
            0
        )

    def test_fusion_conserve_historique_achats(self):
        achat = Achat.objects.create(
            client=self.secondaire,
            type_achat=Achat.TypeAchat.PAYANT
        )

        fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant
        )

        achat.refresh_from_db()

        self.assertEqual(
            achat.client,
            self.secondaire
        )

        self.assertTrue(
            Achat.objects.filter(
                pk=achat.pk
            ).exists()
        )

    
    def test_fusion_cree_mouvements_compensatoires(self):
        fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant,
        )

        mouvements = MouvementFidelite.objects.filter(
            type_mouvement=(
                MouvementFidelite.TypeMouvement.FUSION
            )
        )

        self.assertEqual(mouvements.count(), 2)

        self.assertEqual(
            sum(m.variation_etampes for m in mouvements),
            0,
        )

        self.assertEqual(
            sum(m.variation_recompenses for m in mouvements),
            0,
        )

        self.assertEqual(
            sum(m.variation_dette for m in mouvements),
            0,
        )

    def test_compte_fusionne_refuse_nouvel_achat(self):
        fusionner_clients(
            self.principal.id,
            self.secondaire.id,
            self.gerant,
        )

        self.secondaire.refresh_from_db()

        with self.assertRaises(ValueError):
            enregistrer_achat_payant(
                self.secondaire
            )



class FusionClientInterfaceTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_interface",
            password="Test12345!",
        )

        self.barista = User.objects.create_user(
            username="barista_interface",
            password="Test12345!",
        )

        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        self.gerant.groups.add(groupe_gerant)

        self.principal = Client.objects.create(
            nom="Alice",
            telephone="3333333333",
        )

        self.secondaire = Client.objects.create(
            nom="Alice Dupont",
            telephone="4444444444",
        )

        Fidelite.objects.get_or_create(
            client=self.principal
        )

        Fidelite.objects.get_or_create(
            client=self.secondaire
        )

        self.url = reverse(
            "loyalty:fusion_clients"
        )

    def test_gerant_peut_ouvrir_page(self):
        self.client.force_login(self.gerant)

        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            200
        )

    def test_barista_ne_peut_pas_ouvrir_page(self):
        self.client.force_login(self.barista)

        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            403
        )

    def test_utilisateur_non_connecte_est_redirige(self):
        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            302
        )

    def test_gerant_peut_fusionner_clients(self):
        self.client.force_login(self.gerant)

        reponse = self.client.post(
            self.url,
            {
                "client_principal": self.principal.pk,
                "client_secondaire": self.secondaire.pk,
                "confirmation": "on",
            },
        )

        self.assertEqual(
            reponse.status_code,
            302
        )

        self.secondaire.refresh_from_db()

        self.assertTrue(
            self.secondaire.est_fusionne
        )

        self.assertEqual(
            self.secondaire.fusionne_vers_id,
            self.principal.pk
        )

        self.assertEqual(
            FusionClient.objects.count(),
            1
        )

    def test_formulaire_refuse_meme_client(self):
        self.client.force_login(self.gerant)

        reponse = self.client.post(
            self.url,
            {
                "client_principal": self.principal.pk,
                "client_secondaire": self.principal.pk,
                "confirmation": "on",
            },
        )

        self.assertEqual(
            reponse.status_code,
            200
        )

        self.assertEqual(
            FusionClient.objects.count(),
            0
        )

        self.assertTrue(
            reponse.context["form"].errors
        )



class AnonymisationClientTests(TestCase):

    def setUp(self):
        User = get_user_model()

        # Creer un gerant
        self.gerant = User.objects.create_user(
            username="gerant_anonymisation",
            password="Test12345!",
        )

        # Creer un barista
        self.barista = User.objects.create_user(
            username="barista_anonymisation",
            password="Test12345!",
        )

        # Attribuer le role de gerant
        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        self.gerant.groups.add(groupe_gerant)

        # Creer un client
        self.client_test = Client.objects.create(
            nom="Alice Dupont",
            telephone="5551234567",
            courriel="alice@example.com",
        )

        # Creer son compte de fidelite
        Fidelite.objects.get_or_create(
            client=self.client_test
        )

    def test_anonymisation_efface_donnees_personnelles(self):
        anonymiser_client(
            self.client_test.pk,
            self.gerant,
        )

        self.client_test.refresh_from_db()

        self.assertEqual(
            self.client_test.nom,
            "Client anonymise",
        )

        self.assertIsNone(
            self.client_test.telephone
        )

        self.assertEqual(
            self.client_test.courriel,
            "",
        )

        self.assertTrue(
            self.client_test.est_anonymise
        )

        self.assertIsNotNone(
            self.client_test.date_anonymisation
        )

    def test_anonymisation_conserve_achats(self):
        achat = Achat.objects.create(
            client=self.client_test,
            type_achat=Achat.TypeAchat.PAYANT,
        )

        anonymiser_client(
            self.client_test.pk,
            self.gerant,
        )

        achat.refresh_from_db()

        self.assertEqual(
            achat.client_id,
            self.client_test.pk,
        )

        self.assertTrue(
            Achat.objects.filter(
                pk=achat.pk
            ).exists()
        )

    def test_barista_ne_peut_pas_anonymiser(self):
        with self.assertRaises(PermissionError):
            anonymiser_client(
                self.client_test.pk,
                self.barista,
            )

        self.client_test.refresh_from_db()

        self.assertFalse(
            self.client_test.est_anonymise
        )

        self.assertEqual(
            self.client_test.nom,
            "Alice Dupont",
        )

    def test_impossible_anonymiser_deux_fois(self):
        anonymiser_client(
            self.client_test.pk,
            self.gerant,
        )

        with self.assertRaises(ValueError):
            anonymiser_client(
                self.client_test.pk,
                self.gerant,
            )

    def test_impossible_anonymiser_compte_fusionne(self):
        principal = Client.objects.create(
            nom="Alice Principale",
            telephone="5559876543",
        )

        Fidelite.objects.get_or_create(
            client=principal
        )

        fusionner_clients(
            principal.pk,
            self.client_test.pk,
            self.gerant,
        )

        with self.assertRaises(ValueError):
            anonymiser_client(
                self.client_test.pk,
                self.gerant,
            )

    def test_anonymisation_conserve_cartes(self):
        carte = CartePrepayee.objects.create(
            client=self.client_test,
            cafes_restants=8,
            active=True,
        )

        anonymiser_client(
            self.client_test.pk,
            self.gerant,
        )

        carte.refresh_from_db()

        self.assertEqual(
            carte.client_id,
            self.client_test.pk,
        )

        self.assertEqual(
            carte.cafes_restants,
            8,
        )

        self.assertTrue(
            CartePrepayee.objects.filter(
                pk=carte.pk
            ).exists()
        )



class AnonymisationClientInterfaceTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_interface_anonymisation",
            password="Test12345!",
        )

        self.barista = User.objects.create_user(
            username="barista_interface_anonymisation",
            password="Test12345!",
        )

        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        self.gerant.groups.add(groupe_gerant)

        self.client_test = Client.objects.create(
            nom="Alice Dupont",
            telephone="5551234567",
            courriel="alice@example.com",
        )

        Fidelite.objects.get_or_create(
            client=self.client_test
        )

        self.url = reverse(
            "loyalty:anonymisation_client"
        )

    def test_gerant_peut_ouvrir_page(self):
        self.client.force_login(self.gerant)

        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            200
        )

    def test_barista_ne_peut_pas_ouvrir_page(self):
        self.client.force_login(self.barista)

        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            403
        )

    def test_utilisateur_non_connecte_est_redirige(self):
        reponse = self.client.get(self.url)

        self.assertEqual(
            reponse.status_code,
            302
        )

    def test_gerant_peut_anonymiser_client(self):
        self.client.force_login(self.gerant)

        reponse = self.client.post(
            self.url,
            {
                "client": self.client_test.pk,
                "confirmation": "on",
            },
        )

        self.assertEqual(
            reponse.status_code,
            302
        )

        self.client_test.refresh_from_db()

        self.assertTrue(
            self.client_test.est_anonymise
        )

        self.assertEqual(
            self.client_test.nom,
            "Client anonymise"
        )

        self.assertIsNone(
            self.client_test.telephone
        )

    def test_confirmation_obligatoire(self):
        self.client.force_login(self.gerant)

        reponse = self.client.post(
            self.url,
            {
                "client": self.client_test.pk,
            },
        )

        self.assertEqual(
            reponse.status_code,
            200
        )

        self.client_test.refresh_from_db()

        self.assertFalse(
            self.client_test.est_anonymise
        )

        self.assertTrue(
            reponse.context["form"].errors
        )

    def test_client_deja_anonymise_est_refuse(self):
        self.client_test.est_anonymise = True
        self.client_test.save(
            update_fields=["est_anonymise"]
        )

        self.client.force_login(self.gerant)

        reponse = self.client.post(
            self.url,
            {
                "client": self.client_test.pk,
                "confirmation": "on",
            },
        )

        self.assertEqual(
            reponse.status_code,
            200
        )

        self.assertTrue(
            reponse.context["form"].errors
        )

        self.client_test.refresh_from_db()

        self.assertTrue(
            self.client_test.est_anonymise
        )



class ProtectionClientInactifTests(TestCase):

    def setUp(self):
        self.client_test = Client.objects.create(
            nom="Client Test",
            telephone="5551112222",
        )

        Fidelite.objects.get_or_create(
            client=self.client_test
        )

    def test_client_actif_est_accepte(self):
        resultat = verifier_client_actif(
            self.client_test
        )

        self.assertTrue(resultat)

    def test_client_anonymise_est_refuse(self):
        self.client_test.est_anonymise = True
        self.client_test.save(
            update_fields=["est_anonymise"]
        )

        with self.assertRaises(ValueError):
            verifier_client_actif(
                self.client_test
            )

    def test_client_fusionne_est_refuse(self):
        self.client_test.est_fusionne = True
        self.client_test.save(
            update_fields=["est_fusionne"]
        )

        with self.assertRaises(ValueError):
            verifier_client_actif(
                self.client_test
            )

    def test_achat_client_anonymise_est_refuse(self):
        self.client_test.est_anonymise = True
        self.client_test.save(
            update_fields=["est_anonymise"]
        )

        with self.assertRaises(ValueError):
            enregistrer_achat_payant(
                self.client_test
            )

        self.assertEqual(
            Achat.objects.filter(
                client=self.client_test
            ).count(),
            0
        )

    def test_achat_client_fusionne_est_refuse(self):
        self.client_test.est_fusionne = True
        self.client_test.save(
            update_fields=["est_fusionne"]
        )

        with self.assertRaises(ValueError):
            enregistrer_achat_payant(
                self.client_test
            )

        self.assertEqual(
            Achat.objects.filter(
                client=self.client_test
            ).count(),
            0
        )



class JournalAuditTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_audit",
            password="Test12345!",
        )

    def test_creation_journal_audit(self):
        """
        Verifie qu'une entree d'audit peut etre creee.
        """

        journal = JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.FUSION,
            objet_id=10,
            description="Fusion de clients",
        )

        self.assertEqual(
            journal.action,
            JournalAudit.TypeAction.FUSION,
        )

        self.assertEqual(
            journal.utilisateur,
            self.gerant,
        )

        self.assertEqual(journal.objet_id, 10)

    def test_date_action_automatique(self):
        """
        Verifie que la date est ajoutee automatiquement.
        """

        journal = JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.ANONYMISATION,
            objet_id=20,
        )

        self.assertIsNotNone(journal.date_action)

    def test_utilisateur_facultatif(self):
        """
        Verifie qu'une entree reste possible
        sans utilisateur associe.
        """

        journal = JournalAudit.objects.create(
            utilisateur=None,
            action=JournalAudit.TypeAction.ANNULATION_ACHAT,
            objet_id=30,
        )

        self.assertIsNone(journal.utilisateur)

        self.assertEqual(
            JournalAudit.objects.count(),
            1,
        )

    def test_affichage_journal(self):
        """
        Verifie la representation textuelle du journal.
        """

        journal = JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.REGLE_FIDELITE,
            objet_id=40,
        )

        affichage = str(journal)

        self.assertIn(
            "Modification de regle",
            affichage,
        )



class JournalAuditIntegrationTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_integration",
            password="Test12345!",
        )

        groupe, _ = Group.objects.get_or_create(
            name="Gerant"
        )
        self.gerant.groups.add(groupe)

        self.client1 = Client.objects.create(
            nom="Client Principal",
            telephone="1111111111",
        )

        self.client2 = Client.objects.create(
            nom="Client Secondaire",
            telephone="2222222222",
        )

        Fidelite.objects.get_or_create(
            client=self.client1
        )

        Fidelite.objects.get_or_create(
            client=self.client2
        )

    def test_fusion_cree_journal_audit(self):
        """
        Une fusion reussie doit etre journalisee.
        """

        nombre_avant = JournalAudit.objects.count()

        fusionner_clients(
            client_principal_id=self.client1.pk,
            client_secondaire_id=self.client2.pk,
            gerant=self.gerant,
        )

        self.assertEqual(
            JournalAudit.objects.count(),
            nombre_avant + 1,
        )

        self.assertTrue(
            JournalAudit.objects.filter(
                action=JournalAudit.TypeAction.FUSION,
            ).exists()
        )

    def test_anonymisation_cree_journal_audit(self):
        """
        Une anonymisation reussie doit etre journalisee.
        """

        nombre_avant = JournalAudit.objects.count()

        anonymiser_client(
            client_id=self.client1.pk,
            gerant=self.gerant,
        )

        self.assertEqual(
            JournalAudit.objects.count(),
            nombre_avant + 1,
        )

        self.assertTrue(
            JournalAudit.objects.filter(
                action=JournalAudit.TypeAction.ANONYMISATION,
                objet_id=self.client1.pk,
            ).exists()
        )

    def test_fusion_refusee_ne_cree_pas_audit(self):
        """
        Une fusion invalide ne doit pas produire
        d'audit de fusion reussie.
        """

        nombre_avant = JournalAudit.objects.count()

        with self.assertRaises(ValueError):
            fusionner_clients(
                client_principal_id=self.client1.pk,
                client_secondaire_id=self.client1.pk,
                gerant=self.gerant,
            )

        self.assertEqual(
            JournalAudit.objects.count(),
            nombre_avant,
        )

    def test_anonymisation_refusee_ne_cree_pas_audit(self):
        """
        Une deuxieme anonymisation doit etre refusee
        sans creer un nouvel audit.
        """

        anonymiser_client(
            client_id=self.client1.pk,
            gerant=self.gerant,
        )

        nombre_avant = JournalAudit.objects.count()

        with self.assertRaises(ValueError):
            anonymiser_client(
                client_id=self.client1.pk,
                gerant=self.gerant,
            )

        self.assertEqual(
            JournalAudit.objects.count(),
            nombre_avant,
        )


class JournalAuditInterfaceTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.gerant = User.objects.create_user(
            username="gerant_audit_interface",
            password="Test12345!",
        )

        self.employe = User.objects.create_user(
            username="employe_audit_interface",
            password="Test12345!",
        )

        groupe_gerant, _ = Group.objects.get_or_create(
            name="Gerant"
        )

        self.gerant.groups.add(groupe_gerant)

        self.url = reverse("loyalty:journal_audit")

    def test_gerant_peut_consulter_journal(self):
        """
        Un gerant peut consulter le journal.
        """

        self.client.force_login(self.gerant)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "loyalty/journal_audit.html",
        )

    def test_employe_ne_peut_pas_consulter_journal(self):
        """
        Un employe ordinaire doit recevoir HTTP 403.
        """

        self.client.force_login(self.employe)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_utilisateur_non_connecte_est_redirige(self):
        """
        Un visiteur non connecte doit etre redirige.
        """

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

        self.assertIn(
            "next=",
            response["Location"],
        )

    def test_journal_affiche_operations(self):
        """
        Les operations enregistrees doivent apparaitre.
        """

        JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.FUSION,
            objet_id=15,
            description="Fusion de deux clients",
        )

        self.client.force_login(self.gerant)

        response = self.client.get(self.url)

        self.assertContains(
            response,
            "Fusion de deux clients",
        )

        self.assertContains(
            response,
            "Fusion de clients",
        )

    def test_journal_affiche_plus_recent_en_premier(self):
        """
        Les operations recentes apparaissent en premier.
        """

        ancien = JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.FUSION,
            objet_id=10,
            description="Operation ancienne",
        )

        recent = JournalAudit.objects.create(
            utilisateur=self.gerant,
            action=JournalAudit.TypeAction.ANONYMISATION,
            objet_id=20,
            description="Operation recente",
        )

        maintenant = timezone.now()

        JournalAudit.objects.filter(
            pk=ancien.pk
        ).update(
            date_action=maintenant - timezone.timedelta(days=2)
        )

        JournalAudit.objects.filter(
            pk=recent.pk
        ).update(
            date_action=maintenant
        )

        self.client.force_login(self.gerant)

        response = self.client.get(self.url)

        journaux = list(response.context["journaux"])

        self.assertEqual(journaux[0].pk, recent.pk)
        self.assertEqual(journaux[1].pk, ancien.pk)
