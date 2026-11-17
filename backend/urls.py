from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import (
    LoginView,
    MedicamentoViewSet,
    PedidoViewSet,
    UsuarioOpcaoViewSet,
    conferir_item_pedido,
)

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'medicamentos', MedicamentoViewSet, basename='medicamento')
router.register(r'usuarios', UsuarioOpcaoViewSet, basename='usuario-opcao')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/itens-pedido/<int:item_id>/conferir/', conferir_item_pedido, name='conferir-item'),
]