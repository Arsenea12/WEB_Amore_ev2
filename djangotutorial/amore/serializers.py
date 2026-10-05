from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Choice, Producto, Question, VotoRegistrado


class ProductoSerializer(serializers.ModelSerializer):
    creado_por = serializers.ReadOnlyField(source="creado_por.username")
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id", "nombre", "tipo", "tipo_display", "descripcion",
            "precio", "disponible", "creado_por",
            "fecha_creacion", "fecha_actualizacion",
        ]
        read_only_fields = ["id", "creado_por", "fecha_creacion", "fecha_actualizacion"]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ["id", "question", "choice_text", "votes"]
        read_only_fields = ["id", "votes"]


class ChoiceNestedSerializer(serializers.ModelSerializer):
    """Versión de solo lectura de Choice, usada dentro de QuestionSerializer."""

    class Meta:
        model = Choice
        fields = ["id", "choice_text", "votes"]
        read_only_fields = fields


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceNestedSerializer(many=True, read_only=True)
    was_published_recently = serializers.BooleanField(read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "pub_date", "was_published_recently", "choices"]
        read_only_fields = ["id"]


class VotoSerializer(serializers.Serializer):
    """Serializer de entrada para POST /api/preguntas/{id}/votar/."""

    choice = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all())

    def validate(self, attrs):
        question = self.context["question"]
        if attrs["choice"].question_id != question.id:
            raise serializers.ValidationError("Esa opción no pertenece a esta pregunta.")
        return attrs


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    """Registro de usuarios vía API (queda siempre sin permisos de staff)."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
        )
        user.is_staff = False
        user.is_superuser = False
        user.set_password(validated_data["password"])
        user.save()
        return user
