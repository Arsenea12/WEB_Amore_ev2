from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Choice, Producto, Question


class AutenticacionJWTTests(APITestCase):
    """Criterios 1 y 2: DRF configurado + autenticación funcionando."""

    def setUp(self):
        self.user = User.objects.create_user(username="cliente", password="ClaveSegura123!")

    def test_obtener_token_con_credenciales_validas(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "cliente", "password": "ClaveSegura123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_rechaza_credenciales_invalidas(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "cliente", "password": "clave-incorrecta"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refrescar_token(self):
        obtain = self.client.post(
            reverse("token_obtain_pair"),
            {"username": "cliente", "password": "ClaveSegura123!"},
        )
        response = self.client.post(reverse("token_refresh"), {"refresh": obtain.data["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class ProductoAPITests(APITestCase):
    """Criterios 4, 5 y 6: JSON, endpoints y permisos tipo RESTful."""

    def setUp(self):
        self.staff = User.objects.create_user(username="staffuser", password="ClaveSegura123!", is_staff=True)
        self.comun = User.objects.create_user(username="comun", password="ClaveSegura123!", is_staff=False)
        self.producto = Producto.objects.create(nombre="Ramo de prueba", precio=Decimal("15000"))

    def _token(self, username, password):
        r = self.client.post(reverse("token_obtain_pair"), {"username": username, "password": password})
        return r.data["access"]

    def test_listar_productos_es_publico_y_json(self):
        response = self.client.get("/api/productos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("results", response.data)  # paginado

    def test_crear_producto_sin_token_falla(self):
        response = self.client.post("/api/productos/", {"nombre": "Nuevo", "precio": "9990"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crear_producto_usuario_comun_falla_403(self):
        token = self._token("comun", "ClaveSegura123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/productos/", {"nombre": "Nuevo", "precio": "9990"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_producto_staff_ok_201(self):
        token = self._token("staffuser", "ClaveSegura123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/productos/", {"nombre": "Nuevo ramo", "precio": "12990", "tipo": "ramo"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["creado_por"], "staffuser")

    def test_precio_invalido_rechazado_400(self):
        token = self._token("staffuser", "ClaveSegura123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.post("/api/productos/", {"nombre": "Malo", "precio": "-5"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_producto_staff_204(self):
        token = self._token("staffuser", "ClaveSegura123!")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(f"/api/productos/{self.producto.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Producto.objects.filter(id=self.producto.id).exists())


class VotacionAPITests(APITestCase):
    """Acción extra `votar`: autenticación + restricción de un voto por usuario."""

    def setUp(self):
        self.user = User.objects.create_user(username="votante", password="ClaveSegura123!")
        self.question = Question.objects.create(question_text="¿Flor favorita?", pub_date=timezone.now())
        self.choice = Choice.objects.create(question=self.question, choice_text="Rosa")

    def _token(self):
        r = self.client.post(reverse("token_obtain_pair"), {"username": "votante", "password": "ClaveSegura123!"})
        return r.data["access"]

    def test_votar_sin_token_falla(self):
        response = self.client.post(f"/api/preguntas/{self.question.id}/votar/", {"choice": self.choice.id})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_votar_con_token_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        response = self.client.post(f"/api/preguntas/{self.question.id}/votar/", {"choice": self.choice.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.choice.refresh_from_db()
        self.assertEqual(self.choice.votes, 1)

    def test_votar_dos_veces_el_mismo_usuario_falla(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token()}")
        self.client.post(f"/api/preguntas/{self.question.id}/votar/", {"choice": self.choice.id})
        response = self.client.post(f"/api/preguntas/{self.question.id}/votar/", {"choice": self.choice.id})
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)


class RegistroAPITests(APITestCase):
    def test_registro_crea_usuario_sin_staff(self):
        response = self.client.post(
            "/api/registro/",
            {"username": "nuevo_api", "email": "", "password": "ClaveSegura123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="nuevo_api")
        self.assertFalse(user.is_staff)
