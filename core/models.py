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

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_usuario_set',
        related_query_name='core_usuario',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_usuario_permissions_set',
        related_query_name='core_usuario_permission',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo', 'perfil']

    def __str__(self):
        return f"{self.nome_completo} ({self.perfil})"

class Medicamento(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_estoque = models.IntegerField(default=0)
    lote = models.CharField(max_length=50)
    data_validade = models.DateField()

    def __str__(self):
        return self.nome

class Pedido(models.Model):
    URGENCIA_CHOICES = [('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta')]
    STATUS_CHOICES = [('solicitado', 'Solicitado'), ('em_conferencia', 'Em conferência'), ('atendido', 'Atendido'), ('pendente', 'Pendente')]

    paciente_nome = models.CharField(max_length=255)
    urgencia = models.CharField(max_length=20, choices=URGENCIA_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='solicitado')
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos_criados')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

class ItemPedido(models.Model):
    SITUACAO_CHOICES = [('aguardando', 'Aguardando'), ('entregue', 'Entregue'), ('pendente', 'Pendente'), ('em_falta', 'Em falta')]

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    nome_item = models.CharField(max_length=255)
    quantidade = models.IntegerField()
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='aguardando')
    conferido_por = models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    conferido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('pedido', 'nome_item')