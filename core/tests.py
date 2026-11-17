from rest_framework import status
from rest_framework.test import APITestCase

from .models import ItemPedido, Pedido, Usuario


class PedidoApiTests(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='equipe',
            email='equipe@example.com',
            password='senha-de-teste',
            nome_completo='Equipe de Enfermagem',
            perfil='enfermagem',
        )

    def test_create_pedido_with_item(self):
        response = self.client.post('/api/pedidos/', {
            'paciente_nome': 'Maria da Silva',
            'urgencia': 'alta',
            'solicitante': self.usuario.id,
            'itens': [{'nome_item': 'Dipirona 500 mg', 'quantidade': 2}],
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        pedido = Pedido.objects.get()
        item = ItemPedido.objects.get(pedido=pedido)
        self.assertEqual(pedido.paciente_nome, 'Maria da Silva')
        self.assertEqual(item.nome_item, 'Dipirona 500 mg')
        self.assertEqual(item.quantidade, 2)

        response = self.client.patch(
            f'/api/pedidos/{pedido.id}/',
            {'status': 'em_conferencia'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        pedido.refresh_from_db()
        self.assertEqual(pedido.status, 'em_conferencia')

    def test_user_choices_exclude_inactive_users(self):
        Usuario.objects.create_user(
            username='inativo',
            email='inativo@example.com',
            password='senha-de-teste',
            nome_completo='Usuário Inativo',
            perfil='enfermagem',
            ativo=False,
        )

        response = self.client.get('/api/usuarios/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [user['id'] for user in response.data],
            [self.usuario.id],
        )
