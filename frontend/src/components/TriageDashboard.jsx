import React, { useEffect, useMemo, useState } from 'react';
import api from '../services/api';
import './TriageDashboard.css';

const statusLabels = {
  solicitado: 'Solicitado',
  em_conferencia: 'Em conferência',
  atendido: 'Atendido',
  pendente: 'Pendente',
};

const urgencyLabels = {
  alta: 'Alta',
  media: 'Média',
  baixa: 'Baixa',
};

const initialForm = {
  paciente_nome: '',
  urgencia: 'media',
  solicitante: '',
  nome_item: '',
  quantidade: '1',
};

function mensagemErro(error, fallback) {
  const data = error.response?.data;
  if (typeof data === 'string') return data;
  if (data && typeof data === 'object') {
    const firstError = Object.values(data).flat()[0];
    if (typeof firstError === 'string') return firstError;
  }
  return fallback;
}

export default function TriageDashboard() {
  const [pedidos, setPedidos] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [atualizando, setAtualizando] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState('');
  const [busca, setBusca] = useState('');
  const [filtroStatus, setFiltroStatus] = useState('');
  const [filtroUrgencia, setFiltroUrgencia] = useState('');
  const [formAberto, setFormAberto] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [pedidoAtualizando, setPedidoAtualizando] = useState(null);

  const carregarDados = async (mostrarLoading = false) => {
    if (mostrarLoading) setLoading(true);
    setErro('');

    try {
      const [pedidosResponse, usuariosResponse] = await Promise.all([
        api.get('pedidos/'),
        api.get('usuarios/'),
      ]);
      setPedidos(pedidosResponse.data);
      setUsuarios(usuariosResponse.data);
      setForm((current) => ({
        ...current,
        solicitante: current.solicitante || String(usuariosResponse.data[0]?.id || ''),
      }));
    } catch (error) {
      setErro(mensagemErro(error, 'Não foi possível carregar os dados. Confira se o servidor está funcionando.'));
    } finally {
      setLoading(false);
      setAtualizando(false);
    }
  };

  useEffect(() => {
    carregarDados(true);
  }, []);

  const pedidosFiltrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase('pt-BR');
    return pedidos.filter((pedido) => {
      const correspondeBusca = !termo
        || pedido.paciente_nome.toLocaleLowerCase('pt-BR').includes(termo)
        || String(pedido.id).includes(termo)
        || (pedido.itens || []).some((item) => item.nome_item.toLocaleLowerCase('pt-BR').includes(termo));
      const correspondeStatus = !filtroStatus || pedido.status === filtroStatus;
      const correspondeUrgencia = !filtroUrgencia || pedido.urgencia === filtroUrgencia;
      return correspondeBusca && correspondeStatus && correspondeUrgencia;
    });
  }, [busca, filtroStatus, filtroUrgencia, pedidos]);

  const totais = useMemo(() => ({
    todos: pedidos.length,
    solicitados: pedidos.filter((pedido) => pedido.status === 'solicitado').length,
    conferencia: pedidos.filter((pedido) => pedido.status === 'em_conferencia').length,
    atendidos: pedidos.filter((pedido) => pedido.status === 'atendido').length,
  }), [pedidos]);

  const alterarCampo = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const criarPedido = async (event) => {
    event.preventDefault();
    setSalvando(true);
    setErro('');

    try {
      await api.post('pedidos/', {
        paciente_nome: form.paciente_nome.trim(),
        urgencia: form.urgencia,
        solicitante: Number(form.solicitante),
        itens: [{
          nome_item: form.nome_item.trim(),
          quantidade: Number(form.quantidade),
        }],
      });
      setForm((current) => ({
        ...initialForm,
        solicitante: current.solicitante,
      }));
      setFormAberto(false);
      await carregarDados();
    } catch (error) {
      setErro(mensagemErro(error, 'Não foi possível cadastrar o pedido. Confira os dados e tente novamente.'));
    } finally {
      setSalvando(false);
    }
  };

  const alterarStatus = async (pedido, status) => {
    setPedidoAtualizando(pedido.id);
    setErro('');

    try {
      await api.patch(`pedidos/${pedido.id}/`, { status });
      await carregarDados();
    } catch (error) {
      setErro(mensagemErro(error, 'Não foi possível atualizar o status do pedido.'));
    } finally {
      setPedidoAtualizando(null);
    }
  };

  if (loading) {
    return <main className="dashboard-loading">Carregando painel de pedidos...</main>;
  }

  return (
    <main className="triage-dashboard">
      <header className="dashboard-header">
        <div>
          <div className="brand-eyebrow">FarmaPedido CCC</div>
          <h1>Painel de pedidos</h1>
          <p>Acompanhe as solicitações e atualize cada etapa do atendimento.</p>
        </div>
        <div className="header-actions">
          <button
            className="button button-secondary"
            type="button"
            onClick={() => {
              setAtualizando(true);
              carregarDados();
            }}
            disabled={atualizando}
          >
            {atualizando ? 'Atualizando...' : 'Atualizar'}
          </button>
          <button className="button button-primary" type="button" onClick={() => setFormAberto(!formAberto)}>
            {formAberto ? 'Fechar formulário' : '+ Novo pedido'}
          </button>
        </div>
      </header>

      {erro && (
        <div className="alert-error" role="alert">
          <span>{erro}</span>
          <button type="button" aria-label="Fechar aviso" onClick={() => setErro('')}>×</button>
        </div>
      )}

      {formAberto && (
        <section className="order-form-panel" aria-labelledby="form-title">
          <div className="section-heading">
            <div>
              <span className="section-kicker">Cadastro rápido</span>
              <h2 id="form-title">Novo pedido</h2>
            </div>
            <p>Preencha os dados do paciente e o primeiro item solicitado.</p>
          </div>

          {usuarios.length === 0 ? (
            <div className="empty-users">
              Cadastre um usuário ativo pelo <a href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer">Admin do Django</a> antes de criar pedidos.
            </div>
          ) : (
            <form className="order-form" onSubmit={criarPedido}>
              <label>
                Nome do paciente
                <input
                  autoFocus
                  name="paciente_nome"
                  value={form.paciente_nome}
                  onChange={alterarCampo}
                  placeholder="Ex.: Maria da Silva"
                  required
                  maxLength={255}
                />
              </label>
              <label>
                Prioridade
                <select name="urgencia" value={form.urgencia} onChange={alterarCampo}>
                  <option value="baixa">Baixa</option>
                  <option value="media">Média</option>
                  <option value="alta">Alta</option>
                </select>
              </label>
              <label>
                Solicitado por
                <select name="solicitante" value={form.solicitante} onChange={alterarCampo} required>
                  {usuarios.map((usuario) => (
                    <option key={usuario.id} value={usuario.id}>
                      {usuario.nome_completo} — {usuario.perfil}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Medicamento ou item
                <input
                  name="nome_item"
                  value={form.nome_item}
                  onChange={alterarCampo}
                  placeholder="Ex.: Dipirona 500 mg"
                  required
                  maxLength={255}
                />
              </label>
              <label className="quantity-field">
                Quantidade
                <input
                  name="quantidade"
                  type="number"
                  min="1"
                  value={form.quantidade}
                  onChange={alterarCampo}
                  required
                />
              </label>
              <div className="form-actions">
                <button className="button button-secondary" type="button" onClick={() => setFormAberto(false)}>
                  Cancelar
                </button>
                <button className="button button-primary" type="submit" disabled={salvando || !form.solicitante}>
                  {salvando ? 'Salvando...' : 'Criar pedido'}
                </button>
              </div>
            </form>
          )}
        </section>
      )}

      <section className="summary-grid" aria-label="Resumo dos pedidos">
        <article className="summary-card summary-total">
          <span className="summary-label">Todos os pedidos</span>
          <strong>{totais.todos}</strong>
          <span className="summary-footnote">no sistema</span>
        </article>
        <article className="summary-card summary-new">
          <span className="summary-label">Solicitados</span>
          <strong>{totais.solicitados}</strong>
          <span className="summary-footnote">aguardando análise</span>
        </article>
        <article className="summary-card summary-progress">
          <span className="summary-label">Em conferência</span>
          <strong>{totais.conferencia}</strong>
          <span className="summary-footnote">em atendimento</span>
        </article>
        <article className="summary-card summary-done">
          <span className="summary-label">Atendidos</span>
          <strong>{totais.atendidos}</strong>
          <span className="summary-footnote">concluídos</span>
        </article>
      </section>

      <section className="orders-panel">
        <div className="orders-heading">
          <div>
            <span className="section-kicker">Visão geral</span>
            <h2>Solicitações</h2>
          </div>
          <span className="results-count">{pedidosFiltrados.length} {pedidosFiltrados.length === 1 ? 'pedido' : 'pedidos'}</span>
        </div>

        <div className="filter-bar">
          <label className="search-field">
            <span aria-hidden="true">⌕</span>
            <input
              type="search"
              value={busca}
              onChange={(event) => setBusca(event.target.value)}
              placeholder="Buscar paciente, item ou número..."
              aria-label="Buscar pedidos"
            />
          </label>
          <select aria-label="Filtrar por status" value={filtroStatus} onChange={(event) => setFiltroStatus(event.target.value)}>
            <option value="">Todos os status</option>
            {Object.entries(statusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <select aria-label="Filtrar por prioridade" value={filtroUrgencia} onChange={(event) => setFiltroUrgencia(event.target.value)}>
            <option value="">Todas as prioridades</option>
            {Object.entries(urgencyLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>

        {pedidosFiltrados.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">✓</div>
            <h3>{pedidos.length === 0 ? 'Nenhum pedido por aqui' : 'Nenhum resultado encontrado'}</h3>
            <p>
              {pedidos.length === 0
                ? 'Quando um pedido for cadastrado, ele aparecerá nesta lista.'
                : 'Tente mudar os filtros ou o termo pesquisado.'}
            </p>
            {pedidos.length === 0 && (
              <button className="button button-primary" type="button" onClick={() => setFormAberto(true)}>
                + Cadastrar primeiro pedido
              </button>
            )}
          </div>
        ) : (
          <div className="orders-list">
            {pedidosFiltrados.map((pedido) => (
              <article className="order-card" key={pedido.id}>
                <div className="order-main">
                  <div className="order-title-row">
                    <div>
                      <span className="order-number">Pedido #{pedido.id}</span>
                      <h3>{pedido.paciente_nome}</h3>
                    </div>
                    <span className={`priority-badge priority-${pedido.urgencia}`}>
                      Prioridade {urgencyLabels[pedido.urgencia] || pedido.urgencia}
                    </span>
                  </div>
                  <div className="order-details">
                    <div className="order-items">
                      <span className="detail-label">Itens</span>
                      {(pedido.itens || []).length === 0
                        ? <span>Nenhum item informado</span>
                        : (pedido.itens || []).map((item) => (
                          <span className="item-chip" key={item.id || item.nome_item}>
                            {item.nome_item} <b>× {item.quantidade}</b>
                          </span>
                        ))}
                    </div>
                    <div>
                      <span className="detail-label">Solicitado em</span>
                      <span>{new Date(pedido.criado_em).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })}</span>
                    </div>
                  </div>
                </div>
                <div className="order-status-control">
                  <span className={`status-badge status-${pedido.status}`}>
                    {statusLabels[pedido.status] || pedido.status}
                  </span>
                  <label>
                    <span className="sr-only">Alterar status do pedido #{pedido.id}</span>
                    <select
                      value={pedido.status}
                      disabled={pedidoAtualizando === pedido.id}
                      onChange={(event) => alterarStatus(pedido, event.target.value)}
                    >
                      {Object.entries(statusLabels).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </label>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>
      <footer className="dashboard-footer">FarmaPedido CCC <span>•</span> Painel local de solicitações</footer>
    </main>
  );
}
