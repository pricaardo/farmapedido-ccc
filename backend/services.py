def atualizar_status_pedido(pedido_id):
    from .models import Pedido
    pedido = Pedido.objects.get(id=pedido_id)
    itens = pedido.itens.all()
    
    if all(item.situacao == 'entregue' for item in itens):
        pedido.status = 'atendido'
    elif any(item.situacao in ['pendente', 'em_falta'] for item in itens):
        pedido.status = 'pendente'
    else:
        pedido.status = 'em_conferencia'
    pedido.save()