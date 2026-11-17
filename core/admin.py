from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ItemPedido, Medicamento, Pedido, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Dados do FarmaPedido', {
            'fields': ('nome_completo', 'perfil', 'ativo'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Dados do FarmaPedido', {
            'classes': ('wide',),
            'fields': ('email', 'nome_completo', 'perfil', 'ativo'),
        }),
    )
    list_display = ('email', 'nome_completo', 'perfil', 'ativo', 'is_staff')
    list_filter = ('perfil', 'ativo', 'is_staff')
    search_fields = ('email', 'username', 'nome_completo')


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'quantidade_estoque', 'lote', 'data_validade')
    search_fields = ('nome', 'lote')


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente_nome', 'urgencia', 'status', 'solicitante', 'criado_em')
    list_filter = ('urgencia', 'status')
    search_fields = ('paciente_nome', 'solicitante__email')
    inlines = (ItemPedidoInline,)
