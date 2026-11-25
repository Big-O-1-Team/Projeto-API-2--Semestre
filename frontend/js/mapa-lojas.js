const MapaLojas = {
  mapa: null,
  marcadores: new Map(),

  limpar() {
    if (this.mapa) this.mapa.remove();
    this.mapa = null;
    this.marcadores.clear();
    document.getElementById("mapa-lojas-bloco")?.remove();
  },

  exibir(box, localizacao, lojas, seletor) {
    this.limpar();
    const bloco = document.createElement("div");
    bloco.id = "mapa-lojas-bloco";
    const mapa = document.createElement("div");
    mapa.id = "mapa-lojas";
    mapa.setAttribute("aria-label", "Mapa de lojas parceiras");
    const aviso = document.createElement("p");
    aviso.className = "mapa-aviso";
    aviso.setAttribute("role", "status");
    bloco.append(mapa, aviso);
    box.append(bloco);

    if (!window.L) {
      mapa.hidden = true;
      aviso.textContent = "Mapa indisponível. Escolha pela lista.";
      return;
    }

    const coordenadas = [];
    this.mapa = L.map(mapa, { scrollWheelZoom: false, maxZoom: 19 });
    const instancia = this.mapa;
    const camada = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(instancia);
    camada.on("tileerror", () => {
      if (this.mapa === instancia) aviso.textContent = "Mapa de ruas indisponível. Os marcadores e a lista continuam disponíveis.";
    });

    if (localizacao) {
      const ponto = [localizacao.latitude, localizacao.longitude];
      coordenadas.push(ponto);
      L.marker(ponto, {
        icon: L.divIcon({className: "mapa-pin mapa-pin--usuario", html: '<span aria-hidden="true">●</span>', iconSize: [30, 30], iconAnchor: [15, 15]}),
        title: "Você está aqui", alt: "Você está aqui", zIndexOffset: 1000
      }).addTo(instancia).bindTooltip("Você está aqui", {direction: "top"});
    }

    const unidades = new Map();
    for (const loja of lojas) {
      if (!Number.isFinite(loja.latitude) || !Number.isFinite(loja.longitude)) continue;
      if (!unidades.has(loja.id)) unidades.set(loja.id, []);
      unidades.get(loja.id).push(loja);
    }

    for (const programas of unidades.values()) {
      const loja = programas[0];
      const ponto = [loja.latitude, loja.longitude];
      coordenadas.push(ponto);
      const marcador = L.marker(ponto, {
        icon: L.divIcon({className: "mapa-pin mapa-pin--loja", html: '<span aria-hidden="true">◆</span>', iconSize: [28, 28], iconAnchor: [14, 14]}),
        title: loja.nome, alt: loja.nome
      }).addTo(instancia);
      const popup = document.createElement("div");
      popup.className = "mapa-popup";
      const nome = document.createElement("strong");
      nome.textContent = loja.nome;
      const endereco = document.createElement("p");
      endereco.textContent = loja.endereco + ", " + loja.cidade;
      popup.append(nome, endereco);
      if (loja.distancia_km != null) {
        const distancia = document.createElement("p");
        distancia.textContent = loja.distancia_km.toLocaleString("pt-BR") + " km em linha reta";
        popup.append(distancia);
      }
      for (const programa of programas) {
        const valor = String(programa.id) + ":" + (programa.programa_id || "");
        const botao = document.createElement("button");
        botao.type = "button";
        botao.className = "mapa-selecionar";
        botao.textContent = programa.programa_nome ? "Selecionar " + programa.programa_nome : "Selecionar loja";
        botao.addEventListener("click", () => {
          if (!seletor || !seletor.isConnected) return;
          seletor.value = valor;
          seletor.dispatchEvent(new Event("change", { bubbles: true }));
        });
        popup.append(botao);
        this.marcadores.set(valor, marcador);
      }
      marcador.bindPopup(popup);
    }

    if (!coordenadas.length) {
      this.limpar();
      return;
    }
    if (coordenadas.length === 1) instancia.setView(coordenadas[0], 14);
    else instancia.fitBounds(coordenadas, { padding: [35, 35], maxZoom: 15 });
    const semCoordenadas = lojas.filter(l => !Number.isFinite(l.latitude) || !Number.isFinite(l.longitude)).length;
    if (semCoordenadas) aviso.textContent = semCoordenadas + " opção(ões) sem coordenadas disponíveis na lista.";
    requestAnimationFrame(() => { if (this.mapa === instancia) instancia.invalidateSize(); });
  },

  destacar(valor) {
    const marcador = this.marcadores.get(valor);
    if (marcador && this.mapa) {
      this.mapa.panTo(marcador.getLatLng());
      marcador.openPopup();
    }
  }
};
