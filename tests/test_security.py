import pytest
from rest_framework.test import APIClient
from core.models import ItemPedido, Pedido, Usuario

@pytest.mark.django_db
def test_enfermagem_nao_pode_conferir_item():
    client = APIClient()
    enfermeira = Usuario.objects.create_user(
        username="ana@exemplo.com", 
        email="ana@exemplo.com", 
        password="password123", 
        perfil="enfermagem",
        nome_completo="Ana Souza"
    )
    client.force_authenticate(user=enfermeira)

    pedido = Pedido.objects.create(
        paciente_nome="Paciente de teste",
        urgencia="baixa",
        solicitante=enfermeira,
    )
    item = ItemPedido.objects.create(
        pedido=pedido,
        nome_item="Medicamento de teste",
        quantidade=1,
    )

    response = client.patch(
        f'/api/itens-pedido/{item.id}/conferir/',
        {"situacao": "entregue"},
    )
    assert response.status_code == 403
    assert response.data["erro"] == "Sem permissão para esta ação."