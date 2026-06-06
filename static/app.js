// ==========================
// PREVISÕES IA PREMIUM
// ==========================

function loadPremiumPredictions(){

    const predictions = [
        {
            game:"Manchester City x Arsenal",
            market:"Over 2.5",
            prediction:"FORTE",
            confidence:"92%",
            odd:"1.88",
            signal:"🔥"
        },

        {
            game:"Flamengo x Grêmio",
            market:"Próximo gol Flamengo",
            prediction:"MÉDIA",
            confidence:"78%",
            odd:"2.10",
            signal:"⚡"
        },

        {
            game:"Real Madrid x Barça",
            market:"BTTS SIM",
            prediction:"FORTE",
            confidence:"88%",
            odd:"1.95",
            signal:"🧠"
        }
    ];

    const table = document.getElementById("predTable");

    if(!table) return;

    table.innerHTML = predictions.map(p => `
        <tr>
            <td>${p.game}</td>
            <td>${p.market}</td>
            <td>${p.prediction}</td>
            <td>
                <span class="confidence-live">
                    ${p.confidence}
                </span>
            </td>
            <td class="live-odd">
                ${p.odd}
            </td>
            <td>${p.signal}</td>
        </tr>
    `).join("");
}


// ==========================
// HEATMAP IA
// ==========================

function loadDashboardHeatmap(){

    const heatmap = document.getElementById("dashHeatmap");

    if(!heatmap) return;

const base = Math.floor(Math.random() * 20) + 65;

const intensidadesReaisSimuladas = [
    base + 12,
    base - 5,
    base - 12,
    base + 4,
    base - 8,
    base + 9,

    base - 15,
    base - 3,
    base + 2,
    base + 14,
    base + 7,
    base - 9,

    base - 18,
    base - 10,
    base + 5,
    base + 16,
    base + 20,
    base + 1,

    base - 14,
    base - 6,
    base + 3,
    base + 11,
    base + 15,
    base + 6
];

    let html = "";

    intensidadesReaisSimuladas.forEach(intensity => {
        html += `
            <div 
                class="heat-cell"
                style="
                    background:rgba(0,255,180,${intensity/100});
                "
                title="Intensidade IA: ${intensity}%"
            >
            </div>
        `;
    });

    heatmap.innerHTML = html;
}


// ==========================
// ÚLTIMOS ACERTOS
// ==========================

function loadLastHits(){

    const hits = [
        "✅ Liverpool x Chelsea → Over 2.5",
        "✅ Palmeiras x Boca → BTTS SIM",
        "✅ PSG x Milan → Próximo gol PSG",
        "✅ Inter x Napoli → Over Escanteios",
        "✅ Bayern x Dortmund → Casa vence"
    ];

    const box = document.getElementById("lastHitsFeed");

    if(!box) return;

    box.innerHTML = hits.map(h => `
        <div class="hit-live-item">
            ${h}
        </div>
    `).join("");
}


// ==========================
// LIVE ODDS
// ==========================

function animateOdds(){

    const odds = document.querySelectorAll(".live-odd");

    odds.forEach(o => {

        const current = parseFloat(o.innerText);

        const variation = (Math.random() * 0.08 - 0.04);

        const newOdd = (current + variation).toFixed(2);

        o.innerText = newOdd;

        if(variation > 0){
            o.style.color = "#00ff88";
        }else{
            o.style.color = "#ff4d6d";
        }
    });
}


// ==========================
// START
// ==========================

loadPremiumPredictions();

loadDashboardHeatmap();

loadLastHits();

setInterval(loadDashboardHeatmap,5000);

setInterval(animateOdds,3000);

// ==========================
// ETAPA 4 - AI ENGINE REALTIME
// ==========================

const aiMessages = [
    "IA recalculando mercados ao vivo...",
    "Detectando pressão ofensiva...",
    "Cruzando odds com probabilidade real...",
    "Analisando value bet em tempo real...",
    "Monitorando risco da entrada...",
    "Calculando próximo gol provável..."
];

function rotateAIMessages(){

    const box = document.getElementById("premiumOpportunity");
    if(!box) return;

    const melhorJogo = games.sort(
    (a, b) => b.marketConfidence - a.marketConfidence
)[0];

const msg =
    melhorJogo.home +
    " x " +
    melhorJogo.away +
    " com " +
    melhorJogo.marketConfidence +
    "% de confiança IA";

const momentumIA = melhor?.momentum || 84;
    box.innerHTML = `
        <h3 class="ai-live-text">${msg}</h3>
        <p class="muted">Engine IA ativa cruzando estatísticas, odds e momentum.</p>

        <div class="momentum-box">
            <div class="momentum-label">
                <span>Momentum IA</span>
                <b>${momentumIA}%</b>
            </div>

            <div class="momentum-bar">
                <div 
    class="momentum-fill ${
        momentumIA >= 90
            ? 'momentum-danger'
            : momentumIA >= 80
            ? 'momentum-hot'
            : 'momentum-medium'
    }"
    style="width:${momentumIA}%">
</div>
            </div>
        </div>
    `;
}

function upgradeOddsWithArrows(){
    const odds = document.querySelectorAll(".live-odd");

    odds.forEach(odd => {
        const oldValue = parseFloat(odd.innerText);
        const move = Math.random() > 0.5 ? 0.03 : -0.03;
        const newValue = (oldValue + move).toFixed(2);

        if(move > 0){
            odd.innerHTML = `${newValue} <span class="odd-up">▲</span>`;
        }else{
            odd.innerHTML = `${newValue} <span class="odd-down">▼</span>`;
        }
    });
}

function injectAiScanner(){
    document.querySelectorAll(".command-card").forEach(card => {
        if(!card.classList.contains("scanner-active")){
            card.classList.add("scanner-active");
        }
    });
}

function startEtapa4(){
    injectAiScanner();
    setInterval(upgradeOddsWithArrows, 3000);
}

startEtapa4();

// ==========================
// ETAPA 5 - CENTRAL DE SINAIS IA
// ==========================

function loadSignalCenter(){

    const box = document.getElementById("premiumOpportunity");
    if(!box) return;

    const signals = [
        {
            jogo:"Manchester City x Arsenal",
            mercado:"Over 2.5 Gols",
            confianca:91,
            odd:"1.88",
            oddJusta:"1.62",
            value:"+16%",
            risco:"Médio",
            decisao:"ENTRADA PREMIUM"
        },
        {
            jogo:"Flamengo x Grêmio",
            mercado:"Próximo Gol Flamengo",
            confianca:84,
            odd:"2.05",
            oddJusta:"1.76",
            value:"+14%",
            risco:"Controlado",
            decisao:"ENTRADA AO VIVO"
        },
        {
            jogo:"Real Madrid x Barça",
            mercado:"BTTS SIM",
            confianca:88,
            odd:"1.95",
            oddJusta:"1.68",
            value:"+13%",
            risco:"Médio",
            decisao:"SINAL FORTE"
        }
    ];

    const melhor = window.liveGames && window.liveGames.length
    ? [...window.liveGames].sort((a, b) => b.marketConfidence - a.marketConfidence)[0]
    : null;

const s = melhor ? {
    jogo: `${melhor.home} x ${melhor.away}`,
    mercado: melhor.recommendedMarket || "Mercado em análise",
    confianca: melhor.marketConfidence || 78,
    momentum: melhor.momentum || 84,
    odd: "analisando",
    oddJusta: "IA",
    value: `+${Math.max(8, Math.round((melhor.marketConfidence || 78) / 6))}%`,
    risco: melhor.risk || "Médio",
    decisao:
    melhor.marketConfidence >= 92
        ? "🚨 GOL IMINENTE"
        : melhor.marketConfidence >= 88
        ? "🔥 ENTRADA PREMIUM"
        : melhor.marketConfidence >= 80
        ? "⚡ OPORTUNIDADE FORTE"
        : "📈 MERCADO EM OBSERVAÇÃO"
} : signals[Math.floor(Math.random() * signals.length)];

    box.innerHTML = `
        <div class="signal-premium-card ${
    s.confianca >= 92
        ? 'signal-card-danger'
        : s.confianca >= 88
        ? 'signal-card-hot'
        : ''
}">
<div class="signal-top">
    <span class="signal-badge">🧠 ${s.decisao}</span>
    <span class="signal-live">● LIVE</span>

    ${
        s.confianca >= 92
            ? `<div class="goal-alert-live">
                🚨 IA detecta chance alta de gol nos próximos minutos
               </div>`
            : ""
    }
</div>
            <h3>${s.jogo}</h3>
            <p class="muted">Mercado recomendado pela IA</p>

            <div class="signal-market ${
    s.confianca >= 92
        ? 'market-danger'
        : s.confianca >= 88
        ? 'market-hot'
        : 'market-medium'
}">
    ${s.mercado}
</div>

    <div class="signal-grid">
    <div><small>Confiança</small><b>${s.confianca}%</b></div>
    <div><small>Odd atual</small><b>${s.odd}</b></div>
    <div><small>Odd justa IA</small><b>${s.oddJusta}</b></div>
    <div><small>Value</small><b class="green-text">${s.value}</b></div>
    <div><small>Risco</small><b>${s.risco}</b></div>

    <div>
        <small>Momentum IA</small>
        <b class="${
            s.momentum >= 90
                ? 'danger-text'
                : s.momentum >= 80
                ? 'green-text'
                : ''
        }">
            ${s.momentum}%
        </b>
    </div>
</div>
                  
            <button class="btn small-btn" onclick="alert('Entrada salva no histórico IA')">
                Salvar entrada
            </button>
        </div>
    `;
}

async function carregarLiveGamesParaIA(){
    try{
        const res = await fetch("/api/live");
        const data = await res.json();

        window.liveGames = data.games || [];

        loadSignalCenter();

    }catch(e){
        console.log("Erro ao carregar jogos live para IA:", e);
    }
}

carregarLiveGamesParaIA();
setInterval(carregarLiveGamesParaIA, 15000);


loadSignalCenter();
setInterval(loadSignalCenter, 7000);

// rotateAIMessages desativado porque o card agora é controlado pela Central de Sinais IA
// setInterval(rotateAIMessages, 3500);