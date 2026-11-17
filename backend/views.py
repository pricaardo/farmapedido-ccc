from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import ItemPedido

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