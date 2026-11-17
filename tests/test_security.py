import pytest
from rest_framework.test import APIClient
from backend.models import Usuario

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
    
    response = client.patch('/api/itens/1/conferir/', {"situacao": "entregue"})
    assert response.status_code == 403
    assert response.data["erro"] == "Sem permissão para esta ação."