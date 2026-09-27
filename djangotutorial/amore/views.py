from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone

from .forms import ProductoForm, RegistroForm
from .models import Choice, Producto, Question


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Exige que el usuario esté logueado Y marcado como 'staff' (o superusuario)
    para administrar productos. Un usuario común (por ejemplo, uno que se
    registró él mismo desde el sitio) puede ver el catálogo y loguearse,
    pero no puede crear, editar ni eliminar productos.
    """

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied("Necesitas permisos de staff para administrar productos.")


class IndexView(generic.ListView):
    template_name = "amore/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Retorna las últimas seis preguntas publicadas (sin incluir
        las que están programadas para el futuro).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by(
            "-pub_date"
        )[:6]


class DetailView(generic.DetailView):
    model = Question
    template_name = "amore/detail.html"

    def get_queryset(self):
        """
        Excluye cualquier pregunta que aún no haya sido publicada.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "amore/results.html"

    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    voted_key = f"voted_question_{question.id}"
    if request.session.get(voted_key):
        return render(
            request,
            "amore/detail.html",
            {
                "question": question,
                "error_message": "Ya registramos tu voto en esta encuesta desde esta sesión.",
                "ya_voto": True,
            },
        )

    try:
        selected_choice = question.choices.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "amore/detail.html",
            {
                "question": question,
                "error_message": "No seleccionaste una opción.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        request.session[voted_key] = True
        return HttpResponseRedirect(reverse("amore:results", args=(question.id,)))


def historia(request):
    return render(request, "amore/historia.html")


def contacto(request):
    return render(request, "amore/contacto.html")


class ProductoListView(generic.ListView):
    model = Producto
    template_name = "amore/producto_list.html"
    context_object_name = "productos"
    paginate_by = 9


class ProductoDetailView(generic.DetailView):
    model = Producto
    template_name = "amore/producto_detail.html"
    context_object_name = "producto"


class ProductoCreateView(StaffRequiredMixin, generic.CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "amore/producto_form.html"
    success_url = reverse_lazy("amore:producto_list")

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, "Producto creado correctamente.")
        return super().form_valid(form)


class ProductoUpdateView(StaffRequiredMixin, generic.UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = "amore/producto_form.html"
    success_url = reverse_lazy("amore:producto_list")

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)


class ProductoDeleteView(StaffRequiredMixin, generic.DeleteView):
    model = Producto
    template_name = "amore/producto_confirm_delete.html"
    context_object_name = "producto"
    success_url = reverse_lazy("amore:producto_list")

    def form_valid(self, form):
        messages.success(self.request, "Producto eliminado correctamente.")
        return super().form_valid(form)


def registro(request):
    """Registro público: cualquier visitante puede crear su cuenta (no-staff)."""
    if request.user.is_authenticated:
        return redirect("amore:index")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"¡Bienvenido/a, {user.username}! Tu cuenta se creó correctamente.")
            return redirect("amore:index")
    else:
        form = RegistroForm()
    return render(request, "registration/registro.html", {"form": form})
