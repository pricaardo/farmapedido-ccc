from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        senha = request.data.get('senha')
        user = authenticate(username=email, password=senha)
        
        if user is not None and user.ativo:
            return Response({"mensagem": "Login efetuado com sucesso", "perfil": user.perfil}, status=status.HTTP_200_OK)
        return Response({"erro": "E-mail ou senha incorretos. Confira e tente de novo."}, status=status.HTTP_400_BAD_REQUEST)