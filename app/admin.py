from django.contrib import admin
from django.db.models import Sum
from .models import User, Flow, Accounts


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email")
    search_fields = ("full_name", "email")


@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "id_user",
        "label_name",
        "price",
        "tipo",
        "category",
        "estatus",
        "dateBill",
    )

    search_fields = ("label_name", "category", "tipo")
    list_filter = ("tipo", "category", "estatus", "dateBill")
    ordering = ("-dateBill",)

    # TOTAL NO RODAPÉ
    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(request, request, extra_context)

        try:
            qs = response.context_data["cl"].queryset

            total = qs.aggregate(total=Sum("price"))["total"] or 0
            ganhos = qs.filter(tipo="ganho").aggregate(total=Sum("price"))["total"] or 0
            despesas = qs.filter(tipo="despesa").aggregate(total=Sum("price"))["total"] or 0

            response.context_data["total"] = total
            response.context_data["ganhos"] = ganhos
            response.context_data["despesas"] = despesas

        except:
            pass

        return response


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ("id", "id_user", "bank_name", "coast")
    search_fields = ("bank_name",)
