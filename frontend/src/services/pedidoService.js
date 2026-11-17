import api from './api';

export const pedidoService = {
  async listarPedidos() {
    const response = await api.get('pedidos/');
    return response.data;
  },

  async criarPedido(dadosPedido) {
    const response = await api.post('pedidos/', dadosPedido);
    return response.data;
  },

  async atualizarStatus(id, status) {
    const response = await api.patch(`pedidos/${id}/`, { status });
    return response.data;
  },

  async verificarEstoque() {
    const response = await api.get('medicamentos/estoque/');
    return response.data;
  }
};