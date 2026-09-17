document.addEventListener('DOMContentLoaded', () => {
  const btnSolicitarCartao = document.getElementById('btn-solicitar-cartao');

  if (btnSolicitarCartao) {
    btnSolicitarCartao.addEventListener('click', () => {
      document.getElementById('formulario')?.scrollIntoView({ behavior: 'smooth' });
    });
  }
});

function irParaPasso(numero) {
  document.querySelectorAll('.passo').forEach(el => {
    el.hidden = el.dataset.passo !== String(numero);
  });
  if (typeof Stepper !== 'undefined') {
    Stepper.atualizar(numero);
  }
}