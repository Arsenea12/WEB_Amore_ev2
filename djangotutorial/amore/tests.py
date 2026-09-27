from django.test import TestCase

# Create your tests here.
import datetime

from django.utils import timezone

from .models import Question
from django.urls import reverse

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


def create_question(question_text, days):
    """
    Crea una pregunta con el texto dado y el desfasaje de días
    respecto a la fecha actual (negativo para el pasado, positivo para el futuro).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """Si no existen preguntas, se muestra el mensaje correspondiente."""
        response = self.client.get(reverse("amore:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Todavía no hay encuestas disponibles.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self):
        """Las preguntas con pub_date en el pasado se muestran en la lista."""
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("amore:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self):
        """Las preguntas con pub_date en el futuro no se muestran."""
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("amore:index"))
        self.assertContains(response, "Todavía no hay encuestas disponibles.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self):
        """Si existen preguntas pasadas y futuras, solo se muestran las pasadas."""
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse("amore:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self):
        """La página de índice puede mostrar múltiples preguntas pasadas."""
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse("amore:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        La vista de detalle de una pregunta con pub_date en el futuro
        retorna un error 404 Not Found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("amore:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        La vista de detalle de una pregunta con pub_date en el pasado
        muestra el texto de la pregunta.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("amore:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)