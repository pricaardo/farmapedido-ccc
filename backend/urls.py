from django.contrib import admin
from django.urls import path
from .views import LoginView, conferir_item_pedido

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/login/',
        LoginView.as_view(),
        name='login'
    ),

    path(
        'api/itens/<int:item_id>/conferir/',
        conferir_item_pedido,
        name='conferir_item'
    ),
]