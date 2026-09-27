from django.core.management.base import BaseCommand
from django.utils import timezone

from amore.models import Choice, Question


class Command(BaseCommand):
    help = "Carga las encuestas de ejemplo (generadas con apoyo de IA) en la base de datos activa."

    def handle(self, *args, **options):
        encuestas = [
            {
                "pregunta": "¿Con qué frecuencia te regalan flores?",
                "opciones": [
                    "Varias veces al año",
                    "Solo en ocasiones especiales",
                    "Casi nunca",
                    "Me gusta recibirlas sin motivo",
                ],
            },
            {
                "pregunta": "¿Qué elemento valoras más en un ramo de lujo?",
                "opciones": [
                    "La frescura de las flores",
                    "El diseño y composición",
                    "El empaque y presentación",
                    "La exclusividad de las variedades",
                ],
            },
            {
                "pregunta": "¿Prefieres entrega a domicilio o retiro en atelier?",
                "opciones": ["Domicilio", "Retiro en atelier", "Ambos"],
            },
            {
                "pregunta": "¿Qué flor te representa más?",
                "opciones": ["Rosa", "Lirio", "Peonía", "Lavanda"],
            },
            {
                "pregunta": "¿Para qué ocasión prefieres un ramo Amore Di Ramos?",
                "opciones": ["Cumpleaños", "Matrimonio", "Aniversario", "Solo porque sí"],
            },
            {
                "pregunta": "¿Cuál es tu estilo de ramo favorito?",
                "opciones": ["Clásico", "Moderno", "Silvestre", "Minimalista"],
            },
        ]

        creadas = 0
        for data in encuestas:
            question, created = Question.objects.get_or_create(
                question_text=data["pregunta"],
                defaults={"pub_date": timezone.now()},
            )
            if created:
                creadas += 1
            for texto in data["opciones"]:
                Choice.objects.get_or_create(question=question, choice_text=texto)

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {creadas} encuestas nuevas creadas (de {Question.objects.count()} en total)."
        ))
