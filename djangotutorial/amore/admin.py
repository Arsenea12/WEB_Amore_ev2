
# Register your models here.
from django.contrib import admin
from .models import Choice, Producto, Question, VotoRegistrado


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ["nombre", "tipo", "precio", "disponible", "creado_por", "fecha_creacion"]
    list_filter = ["tipo", "disponible"]
    search_fields = ["nombre", "descripcion"]
    readonly_fields = ["fecha_creacion", "fecha_actualizacion"]


@admin.register(VotoRegistrado)
class VotoRegistradoAdmin(admin.ModelAdmin):
    list_display = ["usuario", "question", "fecha"]
    list_filter = ["fecha"]
    search_fields = ["usuario__username", "question__question_text"]
    readonly_fields = ["fecha"]