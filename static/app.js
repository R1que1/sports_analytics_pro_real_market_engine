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

    const intensidadesReaisSimuladas = [
        92, 78, 65, 84, 71, 88,
        55, 69, 73, 91, 80, 62,
        47, 58, 76, 89, 94, 67,
        52, 61, 70, 83, 86, 75
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

    const msg = aiMessages[Math.floor(Math.random() * aiMessages.length)];

const momentumIA = game.momentum || 84;
    box.innerHTML = `
        <h3 class="ai-live-text">${msg}</h3>
        <p class="muted">Engine IA ativa cruzando estatísticas, odds e momentum.</p>

        <div class="momentum-box">
            <div class="momentum-label">
                <span>Momentum IA</span>
                <b>${momentumIA}%</b>
            </div>

            <div class="momentum-bar">
                <div class="momentum-fill" style="width:${momentumIA}%"></div>
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

    const s = signals[Math.floor(Math.random() * signals.length)];

    box.innerHTML = `
        <div class="signal-premium-card">
            <div class="signal-top">
                <span class="signal-badge">🧠 ${s.decisao}</span>
                <span class="signal-live">● LIVE</span>
            </div>

            <h3>${s.jogo}</h3>
            <p class="muted">Mercado recomendado pela IA</p>

            <div class="signal-market">${s.mercado}</div>

            <div class="signal-grid">
                <div><small>Confiança</small><b>${s.confianca}%</b></div>
                <div><small>Odd atual</small><b>${s.odd}</b></div>
                <div><small>Odd justa IA</small><b>${s.oddJusta}</b></div>
                <div><small>Value</small><b class="green-text">${s.value}</b></div>
                <div><small>Risco</small><b>${s.risco}</b></div>
            </div>

            <button class="btn small-btn" onclick="alert('Entrada salva no histórico IA')">
                Salvar entrada
            </button>
        </div>
    `;
}

loadSignalCenter();
setInterval(loadSignalCenter, 7000);