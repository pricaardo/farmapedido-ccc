from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from .models import ItemPedido, Medicamento, Pedido, Usuario
from rest_framework.serializers import ModelSerializer

# Serializers
class MedicamentoSerializer(ModelSerializer):
    class Meta:
        model = Medicamento
        fields = '__all__'


class ItemPedidoSerializer(ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ('id', 'nome_item', 'quantidade', 'situacao')
        read_only_fields = ('id',)


class PedidoSerializer(ModelSerializer):
    itens = ItemPedidoSerializer(many=True, required=False)

    class Meta:
        model = Pedido
        fields = ('id', 'paciente_nome', 'urgencia', 'status', 'solicitante', 'criado_em', 'atualizado_em', 'itens')
        read_only_fields = ('id', 'criado_em', 'atualizado_em')

    @transaction.atomic
    def create(self, validated_data):
        itens_data = validated_data.pop('itens', [])
        pedido = Pedido.objects.create(**validated_data)
        ItemPedido.objects.bulk_create([
            ItemPedido(pedido=pedido, **item_data)
            for item_data in itens_data
        ])
        return pedido

    def update(self, instance, validated_data):
        if 'itens' in validated_data:
            raise serializers.ValidationError({
                'itens': 'Os itens não podem ser alterados nesta operação.'
            })
        return super().update(instance, validated_data)


class UsuarioOpcaoSerializer(ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'nome_completo', 'perfil')
        read_only_fields = fields

# ViewSets para o Router
class MedicamentoViewSet(viewsets.ModelViewSet):
    queryset = Medicamento.objects.all()
    serializer_class = MedicamentoSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all().order_by('-criado_em')
    serializer_class = PedidoSerializer


class UsuarioOpcaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Usuario.objects.filter(is_active=True, ativo=True).order_by('nome_completo')
    serializer_class = UsuarioOpcaoSerializer


# Autenticação e Regras de Negócio Específicas
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        senha = request.data.get('senha')
        user = authenticate(username=email, password=senha)
        
        if user is not None and user.ativo:
            return Response({"mensagem": "Login efetuado com sucesso", "perfil": user.perfil}, status=status.HTTP_200_OK)
        return Response({"erro": "E-mail ou senha incorretos. Confira e tente de novo."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def conferir_item_pedido(request, item_id):
    if request.user.perfil != 'farmacia':
        return Response({"erro": "Sem permissão para esta ação."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        item = ItemPedido.objects.get(id=item_id)
        nova_situacao = request.data.get('situacao')
        
        item.situacao = nova_situacao
        item.conferido_por = request.user
        item.conferido_em = timezone.now()
        item.save()
        
        return Response({"mensagem": "Item conferido com sucesso", "data_hora": item.conferido_em}, status=status.HTTP_200_OK)
    except ItemPedido.DoesNotExist:
        return Response({"erro": "Item não encontrado."}, status=status.HTTP_404_NOT_FOUND)