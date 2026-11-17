from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    PERFIL_CHOICES = [
        ('enfermagem', 'Enfermagem'),
        ('farmacia', 'Farmácia'),
        ('coordenacao', 'Coordenação'),
    ]
    
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    perfil = models.CharField(max_length=20, choices=PERFIL_CHOICES)
    ativo = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo', 'perfil']

    def __str__(self):
        return f"{self.nome_completo} ({self.perfil})"