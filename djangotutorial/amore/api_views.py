from django.db import IntegrityError
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Choice, Producto, Question, VotoRegistrado
from .permissions import IsStaffOrReadOnly
from .serializers import (
    ChoiceSerializer,
    ProductoSerializer,
    QuestionSerializer,
    UsuarioRegistroSerializer,
    VotoSerializer,
)


class ProductoViewSet(viewsets.ModelViewSet):
    """
    CRUD completo del catálogo de productos.

    - Lectura (GET): pública.
    - Escritura (POST/PUT/PATCH/DELETE): requiere JWT + usuario staff.
    """

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)

    def get_queryset(self):
        qs = super().get_queryset()
        disponible = self.request.query_params.get("disponible")
        tipo = self.request.query_params.get("tipo")
        if disponible is not None:
            qs = qs.filter(disponible=disponible.lower() in ("1", "true", "si", "sí"))
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs


class QuestionViewSet(viewsets.ModelViewSet):
    """
    Encuestas, de solo lectura para el público y editables solo por staff.
    Incluye la acción extra `votar` para registrar un voto autenticado.
    """

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsStaffOrReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def votar(self, request, pk=None):
        """
        POST /api/preguntas/{id}/votar/   body: {"choice": <id>}

        Requiere estar autenticado (JWT). Cada usuario solo puede votar
        una vez por encuesta: se controla con el modelo VotoRegistrado
        (restricción a nivel de base de datos con UniqueConstraint).
        """
        question = self.get_object()
        serializer = VotoSerializer(data=request.data, context={"question": question})
        serializer.is_valid(raise_exception=True)
        choice = serializer.validated_data["choice"]

        try:
            VotoRegistrado.objects.create(usuario=request.user, question=question)
        except IntegrityError:
            return Response(
                {"detail": "Ya votaste en esta encuesta con este usuario."},
                status=status.HTTP_409_CONFLICT,
            )

        choice.votes += 1
        choice.save(update_fields=["votes"])
        return Response(
            {"detail": "Voto registrado.", "choice": choice.id, "votes": choice.votes},
            status=status.HTTP_201_CREATED,
        )


class ChoiceViewSet(viewsets.ModelViewSet):
    """Opciones de encuesta. Lectura pública, escritura solo staff."""

    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        question_id = self.request.query_params.get("question")
        if question_id:
            qs = qs.filter(question_id=question_id)
        return qs


class RegistroAPIView(generics.CreateAPIView):
    """
    POST /api/registro/   body: {"username", "email", "password"}

    Registro público de usuarios vía API (equivalente al /registro/ del
    sitio web). El usuario creado nunca tiene permisos de staff.
    """

    queryset = None
    serializer_class = UsuarioRegistroSerializer
    permission_classes = [AllowAny]
