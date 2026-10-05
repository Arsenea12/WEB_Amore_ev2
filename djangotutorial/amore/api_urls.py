from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register(r"productos", api_views.ProductoViewSet, basename="api-producto")
router.register(r"preguntas", api_views.QuestionViewSet, basename="api-pregunta")
router.register(r"opciones", api_views.ChoiceViewSet, basename="api-opcion")

urlpatterns = [
    path("registro/", api_views.RegistroAPIView.as_view(), name="api-registro"),
    path("", include(router.urls)),
]
