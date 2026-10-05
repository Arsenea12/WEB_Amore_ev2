import datetime
from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField("Texto de la pregunta", max_length=200)
    pub_date = models.DateTimeField("Fecha de publicación")

    class Meta:
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="¿Publicada recientemente?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices",
        verbose_name="Pregunta"
    )
    choice_text = models.CharField("Texto de la opción", max_length=200)
    votes = models.IntegerField("Votos", default=0)

    class Meta:
        verbose_name = "Opción"
        verbose_name_plural = "Opciones"

    def __str__(self):
        return self.choice_text


class Producto(models.Model):
    TIPO_CHOICES = [
        ("ramo", "Ramo"),
        ("arreglo", "Arreglo floral"),
        ("planta", "Planta"),
        ("accesorio", "Accesorio"),
    ]

    nombre = models.CharField("Nombre", max_length=120)
    tipo = models.CharField("Tipo", max_length=20, choices=TIPO_CHOICES, default="ramo")
    descripcion = models.TextField("Descripción", blank=True)
    precio = models.DecimalField("Precio", max_digits=10, decimal_places=2)
    disponible = models.BooleanField("Disponible", default=True)
    creado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos",
        verbose_name="Creado por",
    )
    fecha_creacion = models.DateTimeField("Fecha de creación", auto_now_add=True)
    fecha_actualizacion = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return self.nombre


class VotoRegistrado(models.Model):
    """
    Registra que un usuario (autenticado vía JWT) ya votó en una encuesta,
    para que la API pueda rechazar un segundo voto del mismo usuario.
    Es el equivalente, para la API, de la restricción por sesión que usa
    el sitio web normal (ver vote() en views.py).
    """

    usuario = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="votos_api",
        verbose_name="Usuario",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="votos_registrados",
        verbose_name="Pregunta",
    )
    fecha = models.DateTimeField("Fecha del voto", auto_now_add=True)

    class Meta:
        verbose_name = "Voto registrado (API)"
        verbose_name_plural = "Votos registrados (API)"
        constraints = [
            models.UniqueConstraint(fields=["usuario", "question"], name="un_voto_por_usuario_y_pregunta")
        ]

    def __str__(self):
        return f"{self.usuario} votó en '{self.question}'"