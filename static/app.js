
let currentUser = null;
let iaChart, statsChart, pieChart;

const links = document.querySelectorAll("nav a[data-page]");
const pages = document.querySelectorAll(".page");

function goPage(pageId){
  pages.forEach(p => p.classList.remove("active"));
  document.getElementById(pageId).classList.add("active");
  links.forEach(a => a.classList.toggle("active", a.dataset.page === pageId));
  document.getElementById("sidebar").classList.remove("open");
  window.scrollTo({top:0,behavior:"smooth"});
  if(pageId === "admin") loadAdmin();
  if(pageId === "estatisticas") renderExtraCharts();
  if(pageId === "radar") loadRadar();
  if(pageId === "aprendizado") loadML();
  if(pageId === "favoritos") loadFavorites();
  if(pageId === "avancado") loadAdvancedStats();
  if(pageId === "odds") loadOdds();
  if(pageId === "heatmap") loadHeatmap();
  if(pageId === "financeiro") loadFinancial();
  if(pageId === "deploy") loadDeploy();
  if(pageId === "cloudPro") loadCloudHealth();
  if(pageId === "realEngine") loadRealOddsPremium();
  if(pageId === "arbitragem") runArbitrage();
  if(pageId === "deployReal") loadDeployReal();
  if(pageId === "mlReal") trainRealML();
  if(pageId === "realtime") requestLiveTick();
  if(pageId === "entradas") loadEntries();
  if(pageId === "treino") trainContinuous();
  if(pageId === "apiSistema") loadSystemHealth();
}

links.forEach(link => link.addEventListener("click", () => goPage(link.dataset.page)));

function toggleMenu(){ document.getElementById("sidebar").classList.toggle("open"); }

async function login(){
  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;
  const r = await fetch("/api/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email,password})
  });
  const data = await r.json();
  if(!data.ok){
    document.getElementById("loginMsg").innerText = data.error || "Erro ao entrar";
    return;
  }
  await boot();
}

function loginAdmin(){
  document.getElementById("loginEmail").value = "admin@sportspro.com";
  document.getElementById("loginPassword").value = "admin123";
  login();
}

async function logout(){
  await fetch("/api/logout", {method:"POST"});
  location.reload();
}

async function boot(){
  const r = await fetch("/api/me");
  const data = await r.json();
  if(!data.logged) return;

  currentUser = data.user;
  document.getElementById("loginScreen").style.display = "none";
  document.getElementById("app").style.display = "grid";
  document.getElementById("userName").innerText = currentUser.name;
  document.getElementById("userPlan").innerText = currentUser.plan;

  if(currentUser.role === "admin"){
    document.getElementById("adminMenu").style.display = "flex";
  }

  await loadStats();
  await loadLive();
  await loadAlerts();
  fillPredictions();
}

async function loadStats(){
  const r = await fetch("/api/stats");
  const s = await r.json();
  document.getElementById("accuracy").innerText = s.accuracy + "%";
  document.getElementById("profit").innerText = "+" + s.profit + "%";
  document.getElementById("profit2").innerText = "+" + s.profit + "%";
  document.getElementById("roi").innerText = "+" + s.roi + "%";
  document.getElementById("roi2").innerText = "+" + s.roi + "%";
  document.getElementById("operations").innerText = s.operations;
  document.getElementById("goals").innerText = s.goals;
  document.getElementById("corners").innerText = s.corners;
  document.getElementById("cards").innerText = s.cards;
  document.getElementById("possession").innerText = s.possession + "%";

  const ctx = document.getElementById("iaChart");
  if(iaChart) iaChart.destroy();
  iaChart = new Chart(ctx, {
    type:"line",
    data:{
      labels:["14/05","15/05","16/05","17/05","18/05","19/05","20/05","21/05"],
      datasets:[{label:"Lucro IA",data:s.chart,borderColor:"#b936ff",backgroundColor:"rgba(139,44,255,.25)",fill:true,tension:.35}]
    },
    options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}},y:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}}}}
  });
}

async function loadLive(){
  
document.getElementById("allGames").innerHTML = `
<div class="loading-live">

    <div class="loading-card"></div>
    <div class="loading-card"></div>
    <div class="loading-card"></div>

</div>
`;

  const r = await fetch("/api/live");
  const data = await r.json();
  const games = data.games || [];
  document.getElementById("liveCount").innerText = games.filter(g=>g.live).length + " AO VIVO";

const liveStatus = document.getElementById("liveUpdateStatus");

if(liveStatus){
  liveStatus.innerText = "⚡ Realtime atualizado " + new Date().toLocaleTimeString("pt-BR");
}

  const html = games.map(g => matchCard(g)).join("");
  document.getElementById("livePreview").innerHTML = games.slice(0,3).map(g => matchCard(g)).join("");
  const gamesContainer =
document.getElementById("allGames");

gamesContainer.innerHTML = html;

document
.querySelectorAll(".live-card")
.forEach(card => {

    card.classList.add("updated");

    setTimeout(() => {
        card.classList.remove("updated");
    }, 1200);

});
}

function logoOrBall(url){
  return url ? `<img class="badge-img" src="${url}">` : `<div class="badge-img"></div>`;
}

function matchCard(g){
  return `
<div class="live-card ${(g.marketConfidence || 70) >= 85 ? 'danger-live' : ''}"
onclick="this.classList.toggle('expanded')">

    <div class="live-top">

        <span class="league-name">${g.league}</span>

        <span class="status-live">
            ${g.status || 'LIVE'}
        </span>

    </div>

    <div class="teams-live">

        <div class="team-live">
            <img
                loading="lazy"
                src="${g.homeLogo || 'https://cdn-icons-png.flaticon.com/512/53/53283.png'}"
                class="team-logo"
            >

            <span>${g.home}</span>
        </div>

        <div class="score-live">
            ${g.homeGoals ?? 0}
            <small>x</small>
            ${g.awayGoals ?? 0}
        </div>

        <div class="team-live">
            <img
                loading="lazy"
                src="${g.awayLogo || 'https://cdn-icons-png.flaticon.com/512/53/53283.png'}"
                class="team-logo"
            >

            <span>${g.away}</span>
        </div>

    </div>

    <div class="pressure-wrapper">

        <div class="pressure-label">
            🔥 Pressão IA
        </div>

        <div class="pressure-bar">
            <div
                class="pressure-fill"
                style="width:${g.marketConfidence || 70}%">
            </div>
        </div>

        <div class="pressure-percent">
            ${g.marketConfidence || 70}%
        </div>

    </div>

    <div class="ai-box">

        <div class="ai-title">
            🧠 IA ELITE
        </div>

        <div class="ai-analysis">
            ${g.aiAnalysis || 'IA analisando partida...'}
        </div>

        <div class="market-tag">
            ${g.recommendedMarket || 'Over 1.5 gols'}
        </div>

    </div>

    <div class="expand-section">

        <div class="expand-title">
            📊 Estatísticas Premium
        </div>

        <div class="stats-grid">

            <div class="stat-item">
                <span>Posse</span>
                <strong>${g.home_stats?.possession || 0}%</strong>
            </div>

            <div class="stat-item">
                <span>Chutes</span>
                <strong>${g.home_stats?.shots || 0}</strong>
            </div>

            <div class="stat-item">
                <span>No alvo</span>
                <strong>${g.home_stats?.shots_on_goal || 0}</strong>
            </div>

            <div class="stat-item">
                <span>Escanteios</span>
                <strong>${g.home_stats?.corners || 0}</strong>
            </div>

            <div class="stat-item">
                <span>Ataques perigosos</span>
                <strong>${g.home_stats?.dangerous_attacks || 0}</strong>
            </div>

        </div>

    </div>

</div>
`;
}

function fillPredictions(){
  const rows = [
    ["Man City vs Real Madrid","1X2 - Casa","Man City","92%","1.72"],
    ["PSG vs Bayern","Ambos marcam","Sim","89%","1.68"],
    ["Flamengo vs Palmeiras","Mais de 1.5 gols","Sim","87%","1.57"],
    ["Liverpool vs Chelsea","Dupla Chance","1X","85%","1.44"],
    ["Barcelona vs Atlético","Mais de 2.5 gols","Sim","84%","1.60"],
  ];
  document.getElementById("predTable").innerHTML = rows.map(r => `
    <tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td><span class="confidence">${r[3]}</span></td><td>${r[4]}</td><td class="signal">▮▮▮</td></tr>
  `).join("");
}

async function gerarPrevisao(){
  const home = document.getElementById("homeTeam").value;
  const away = document.getElementById("awayTeam").value;

  const r = await fetch("/api/elite-analysis", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({home,away})
  });
  const p = await r.json();

  document.getElementById("resultadoIA").innerHTML = `
    <div class="card-title"><h2>IA Elite Agressiva</h2><span class="pill green">${p.source}</span></div>
    <h2 class="purple-text">${p.favorite} favorito</h2><br>
    <div class="mini-stats">
      <div><small>${p.home}</small><h3>${p.home_prob}%</h3></div>
      <div><small>EMPATE</small><h3>${p.draw_prob}%</h3></div>
      <div><small>${p.away}</small><h3>${p.away_prob}%</h3></div>
      <div><small>CONFIANÇA</small><h3>${p.confidence}%</h3></div>
    </div>
    <br>
    <div class="box">
      <b>Leitura agressiva:</b><br><br>
      ${p.explanation.map(x => `<p>⚡ ${x}</p>`).join("")}
    </div>
    <br>
    <div class="box">
      <b>Mercados sugeridos pela IA:</b><br><br>
      ${p.markets.map(m => `<p>✅ ${m.market} — <b>${m.confidence}%</b> | Risco: ${m.risk} <button class="btn small-btn" onclick="saveFavorite('${p.home}','${p.away}','${m.market}',${m.confidence})">Salvar</button></p>`).join("")}
    </div>
    <br>
    <div class="two">
      <div class="box">
        <b>${p.home}</b><br><br>
        <p>Gols feitos: ${p.home_form.avg_goals_for}</p>
        <p>Gols sofridos: ${p.home_form.avg_goals_against}</p>
        <p>BTTS: ${p.home_form.btts_rate}%</p>
        <p>Over 2.5: ${p.home_form.over25_rate}%</p>
        <p>Forma: ${p.home_form.form_score}%</p>
      </div>
      <div class="box">
        <b>${p.away}</b><br><br>
        <p>Gols feitos: ${p.away_form.avg_goals_for}</p>
        <p>Gols sofridos: ${p.away_form.avg_goals_against}</p>
        <p>BTTS: ${p.away_form.btts_rate}%</p>
        <p>Over 2.5: ${p.away_form.over25_rate}%</p>
        <p>Forma: ${p.away_form.form_score}%</p>
      </div>
    </div>
    <br>
    <div class="box">
      <b>Confronto direto:</b>
      <p>${p.h2h.games} jogos encontrados | ${p.home}: ${p.h2h.home_wins} vitórias | Empates: ${p.h2h.draws} | ${p.away}: ${p.h2h.away_wins} vitórias</p>
      <br>
      <b>Índices de mercado:</b>
      <p>Expectativa de gols: ${p.expected_goals}</p>
      <p>Índice BTTS: ${p.btts_index}%</p>
      <p>Índice Over 2.5: ${p.over25_index}%</p>
      <p>Risco geral: ${p.risk}</p>
    </div>
  `;
}

async function loadAlerts(){
  const r = await fetch("/api/alerts");
  const alerts = await r.json();
  const html = alerts.map(a => `
    <div class="row">
      <span>${a.title}<br><small class="muted">${a.description}</small></span>
      <b class="confidence">${a.confidence}%</b>
    </div>
  `).join("");
  document.getElementById("alertsPreview").innerHTML = html.slice(0, 900);
  document.getElementById("alertsList").innerHTML = html;
}

async function loadAdmin(){
  const r = await fetch("/api/admin/users");
  const data = await r.json();

  if(data.error){
    document.getElementById("adminUsers").innerHTML = `<p class="red">${data.error}</p>`;
    return;
  }

  document.getElementById("adminUsers").innerHTML = `
    <table>
      <thead><tr><th>ID</th><th>Nome</th><th>Email</th><th>Plano</th><th>Função</th><th>Ação</th></tr></thead>
      <tbody>
        ${data.map(u => `
          <tr>
            <td>${u.id}</td>
            <td>${u.name}</td>
            <td>${u.email}</td>
            <td>${u.plan}</td>
            <td>${u.role}</td>
            <td><button class="btn small-btn" onclick="upgradeUser(${u.id})">Premium</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function upgradeUser(id){
  await fetch("/api/admin/upgrade", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({user_id:id, plan:"VIP PREMIUM"})
  });
  loadAdmin();
}

async function renderExtraCharts(){
  const r = await fetch("/api/stats");
  const s = await r.json();

  const ctx1 = document.getElementById("statsChart");
  if(statsChart) statsChart.destroy();
  statsChart = new Chart(ctx1, {
    type:"bar",
    data:{labels:["Gols","Escanteios","Cartões","Posse"],datasets:[{label:"Métricas",data:[s.goals,s.corners,s.cards,s.possession],backgroundColor:"rgba(185,54,255,.7)"}]},
    options:{responsive:true,plugins:{legend:{labels:{color:"#fff"}}},scales:{x:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}},y:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}}}}
  });

  const ctx2 = document.getElementById("pieChart");
  if(pieChart) pieChart.destroy();
  pieChart = new Chart(ctx2, {
    type:"doughnut",
    data:{labels:["Casa","Empate","Fora","Over 2.5"],datasets:[{data:[45,25,20,10],backgroundColor:["#8b2cff","#6a24d8","#421278","#c037ff"]}]},
    options:{responsive:true,plugins:{legend:{labels:{color:"#fff"}}}}
  });
}

boot();
setInterval(loadLiveGames, 180000);
(loadAlerts, 15000);


async function loadRadar(){
  const box = document.getElementById("radarList");
  if(!box) return;
  box.innerHTML = "<p class='muted'>Buscando oportunidades...</p>";
  const r = await fetch("/api/ultra-radar");
  const data = await r.json();

  box.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Jogo</th><th>Mercado</th><th>Prob.</th><th>Odd</th><th>Odd justa</th><th>Value</th><th>Heat</th><th>Risco</th><th></th>
        </tr>
      </thead>
      <tbody>
        ${data.map(x => `
          <tr>
            <td>${x.fixture}<br><small class="muted">${x.reason}</small></td>
            <td>${x.market}</td>
            <td>${x.probability}%</td>
            <td>${x.odd}</td>
            <td>${x.fair_odd}</td>
            <td><span class="confidence">${x.value_score}</span></td>
            <td>${x.goal_heat}%</td>
            <td>${x.risk}</td>
            <td><button class="btn small-btn" onclick="saveFavorite('${x.home}','${x.away}','${x.market}',${x.probability})">Salvar</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function loadML(){
  const box = document.getElementById("mlResult");
  if(!box) return;
  box.innerHTML = "<p class='muted'>Analisando histórico...</p>";
  const r = await fetch("/api/ml-learn");
  const x = await r.json();

  box.innerHTML = `
    <div class="card-title"><h2>Resultado do Aprendizado</h2><span class="pill">${x.trained ? "TREINADO" : "SEM DADOS"}</span></div>
    <h1 class="purple-text">${x.accuracy}%</h1>
    <p class="muted">${x.message}</p>
    <br>
    <div class="mini-stats">
      <div><small>AMOSTRA</small><h3>${x.sample}</h3></div>
      <div><small>MELHOR MERCADO</small><h3 style="font-size:16px">${x.best_market}</h3></div>
      <div><small>STATUS</small><h3 style="font-size:16px">${x.trained ? "Ativo" : "Inicial"}</h3></div>
      <div><small>RISCO</small><h3 style="font-size:16px">Controlado</h3></div>
    </div>
    <br>
    <div class="box">
      <b>Regras aprendidas:</b><br><br>
      ${(x.rules || []).map(r => `<p>🧠 ${r}</p>`).join("")}
    </div>
  `;
}

async function saveFavorite(home, away, market, confidence){
  await fetch("/api/save-favorite", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({home,away,market,confidence})
  });
  alert("Favorito salvo com sucesso!");
}

async function loadFavorites(){
  const box = document.getElementById("favList");
  if(!box) return;
  const r = await fetch("/api/favorites");
  const data = await r.json();

  if(!data.length){
    box.innerHTML = "<p class='muted'>Nenhum favorito salvo ainda.</p>";
    return;
  }

  box.innerHTML = data.map(f => `
    <div class="row">
      <span>⭐ ${f.home} x ${f.away}<br><small class="muted">${f.market}</small></span>
      <b class="confidence">${f.confidence}%</b>
    </div>
  `).join("");
}

async function gerarPushAlerts(){
  await fetch("/api/push-alerts");
  alert("Alertas inteligentes criados!");
  loadAlerts();
}


let financialChart;

async function loadAdvancedStats(){
  const team = document.getElementById("advTeam")?.value || "Manchester City";
  const box = document.getElementById("advancedStatsBox");
  if(!box) return;
  const r = await fetch("/api/advanced-stats?team=" + encodeURIComponent(team));
  const s = await r.json();
  box.innerHTML = `
    <div class="card-title"><h2>${s.team}</h2><span class="pill">Avançado</span></div>
    <div class="mini-stats">
      <div><small>xG</small><h3>${s.xg}</h3></div>
      <div><small>xGA</small><h3>${s.xga}</h3></div>
      <div><small>Chutes gol</small><h3>${s.shots_on_target}</h3></div>
      <div><small>Escanteios</small><h3>${s.corners}</h3></div>
    </div>
    <br>
    <div class="box">
      <p>Cartões: ${s.cards}</p>
      <p>Ataques perigosos: ${s.dangerous_attacks}</p>
      <p>Posse: ${s.possession}%</p>
      <p>Lesões: ${s.injuries}</p>
      <p>Forma: ${s.form}</p>
      <br><small class="muted">${s.note}</small>
    </div>
  `;
}

async function loadOdds(){
  const box = document.getElementById("oddsBox");
  if(!box) return;
  const r = await fetch("/api/real-odds");
  const data = await r.json();
  box.innerHTML = `
    <table>
      <thead><tr><th>Jogo</th><th>Casa</th><th>Mercado</th><th>Odd</th><th>Odd Justa</th><th>Valor</th></tr></thead>
      <tbody>
        ${data.map(o => `
          <tr>
            <td>${o.fixture}</td><td>${o.bookmaker}</td><td>${o.market}</td>
            <td>${o.odd}</td><td>${o.fair}</td><td><span class="confidence">${o.value}</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function simulateScore(){
  const home = document.getElementById("scoreHome").value;
  const away = document.getElementById("scoreAway").value;
  const r = await fetch("/api/score-simulator", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({home,away})
  });
  const s = await r.json();
  document.getElementById("scoreBox").innerHTML = `
    <div class="card-title"><h2>Placar provável</h2><span class="pill">Simulado</span></div>
    <h1 class="purple-text">${s.score}</h1><br>
    ${s.scenarios.map(x => `
      <div class="row"><span>${x.name}<br><small class="muted">${x.score}</small></span><b class="confidence">${x.chance}%</b></div>
    `).join("")}
  `;
}

async function loadHeatmap(){
  const box = document.getElementById("heatmapBox");
  if(!box) return;
  const r = await fetch("/api/heatmap");
  const data = await r.json();
  const cells = data.zones.flat();
  box.innerHTML = cells.map(v => {
    const cls = v > 70 ? "heat-high" : v > 40 ? "heat-mid" : "heat-low";
    return `<div class="heat-cell ${cls}">${v}</div>`;
  }).join("");
}

async function loadFinancial(){
  const r = await fetch("/api/financial");
  const f = await r.json();
  const summary = document.getElementById("financialSummary");
  if(!summary) return;
  summary.innerHTML = `
    <div class="card-title"><h2>Resultado</h2><span class="pill">ROI</span></div>
    <h1 class="${f.total >= 0 ? 'green' : 'red'}">R$ ${f.total}</h1>
    <br>
    <div class="mini-stats">
      <div><small>Wins</small><h3>${f.wins}</h3></div>
      <div><small>Losses</small><h3>${f.losses}</h3></div>
      <div><small>Total</small><h3>${f.history.length}</h3></div>
      <div><small>Status</small><h3 style="font-size:16px">${f.total >= 0 ? 'Lucro' : 'Prejuízo'}</h3></div>
    </div>
  `;
  document.getElementById("financialHistory").innerHTML = f.history.map(h => `
    <div class="row"><span>${h.description}<br><small class="muted">${h.created_at}</small></span><b class="${h.amount >= 0 ? 'green' : 'red'}">R$ ${h.amount}</b></div>
  `).join("");

  const ctx = document.getElementById("financialChart");
  if(financialChart) financialChart.destroy();
  financialChart = new Chart(ctx, {
    type:"line",
    data:{labels:f.history.map((_,i)=>i+1),datasets:[{label:"Resultado",data:f.history.map(x=>x.amount),borderColor:"#b936ff",backgroundColor:"rgba(139,44,255,.25)",fill:true,tension:.35}]},
    options:{plugins:{legend:{labels:{color:"#fff"}}},scales:{x:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}},y:{ticks:{color:"#aaa"},grid:{color:"#1b1430"}}}}
  });
}

async function createPix(){
  const r = await fetch("/api/create-pix", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({plan:"VIP PREMIUM"})
  });
  const p = await r.json();
  const box = document.getElementById("pixBox");
  if(!p.ok){
    box.innerHTML = `<p class="red">${p.error}</p>`;
    return;
  }
  box.innerHTML = `
    <br><div class="box">
      <b>PIX ${p.mode === "real" ? "REAL" : "DEMO"} gerado</b>
      <p>Plano: ${p.plan}</p>
      <p>Valor: R$ ${p.amount}</p>
      <div class="pix-code">${p.qr_code}</div>
    </div>
  `;
}

async function loadDeploy(){
  const r = await fetch("/api/deploy-checklist");
  const data = await r.json();
  document.getElementById("deployBox").innerHTML = data.map(x => `
    <div class="row"><span>${x.item}</span><b class="pill">${x.status}</b></div>
  `).join("") + `
    <br><div class="box">
      <b>Mobile/PWA:</b>
      <p>O projeto já está preparado para virar app com WebView ou PWA. Para app nativo, o próximo passo é criar um wrapper com Capacitor.</p>
    </div>
  `;
}


// =========================
// ULTIMATE REALTIME JS
// =========================
let socket = null;

function initSocket(){
  if(typeof io === "undefined") return;
  socket = io();

  socket.on("connect", () => {
    const s = document.getElementById("wsStatus");
    if(s) s.innerText = "Online";
  });

  socket.on("server_status", (data) => {
    addLiveFeed("✅ " + data.message);
  });

  socket.on("live_tick", (data) => {
    renderLiveEvent(data);
    addLiveFeed(`⚡ ${data.timestamp} - ${data.fixture}: ${data.event} (${data.confidence}%)`);
  });
}

function requestLiveTick(){
  if(socket && socket.connected){
    socket.emit("request_live_tick");
  }else{
    fetch("/api/realtime-tick").then(r=>r.json()).then(renderLiveEvent);
  }
}

function renderLiveEvent(e){
  const box = document.getElementById("liveEventBox");
  if(!box) return;
  box.innerHTML = `
    <div class="box">
      <div class="card-title"><h2>${e.fixture}</h2><span class="pill">${e.minute}'</span></div>
      <h1 class="purple-text">${e.score}</h1>
      <p>Evento: <b>${e.event}</b></p>
      <p>Confiança: <b>${e.confidence}%</b></p>
      <p>Pressão ofensiva: ${e.pressure}%</p>
      <div class="bar"><div style="width:${e.pressure}%"></div></div>
      <small class="muted">${e.timestamp}</small>
    </div>
  `;
}

function addLiveFeed(text){
  const feed = document.getElementById("liveFeed");
  if(!feed) return;
  feed.innerHTML = `<div class="row"><span>${text}</span></div>` + feed.innerHTML;
}

setInterval(() => {
  const page = document.getElementById("realtime");
  if(page && page.classList.contains("active")) requestLiveTick();
}, 8000);

async function calcStake(){
  const bankroll = document.getElementById("bankroll").value;
  const probability = document.getElementById("stakeProb").value;
  const odd = document.getElementById("stakeOdd").value;
  const r = await fetch("/api/stake", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({bankroll, probability, odd})
  });
  const s = await r.json();
  document.getElementById("stakeResult").innerHTML = `
    <div class="card-title"><h2>Stake Recomendada</h2><span class="pill">${s.risk}</span></div>
    <h1 class="purple-text">R$ ${s.stake}</h1>
    <p>Banca: R$ ${s.bankroll}</p>
    <p>Probabilidade: ${s.probability}%</p>
    <p>Odd: ${s.odd}</p>
    <p>Método: ${s.method}</p>
    <br><small class="muted">${s.note}</small>
  `;
}

async function quickSaveEntry(){
  const stakeR = await fetch("/api/stake", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({bankroll:1000, probability:62, odd:1.80})
  });
  const s = await stakeR.json();
  await fetch("/api/save-entry", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      fixture:"Manchester City x Real Madrid",
      market:"Mais de 1.5 gols",
      odd:1.80,
      probability:62,
      stake:s.stake
    })
  });
  loadEntries();
}

async function loadEntries(){
  const box = document.getElementById("entriesBox");
  if(!box) return;
  const r = await fetch("/api/entries");
  const data = await r.json();
  if(!data.length){
    box.innerHTML = "<p class='muted'>Nenhuma entrada salva ainda.</p>";
    return;
  }
  box.innerHTML = `
    <table>
      <thead><tr><th>Jogo</th><th>Mercado</th><th>Odd</th><th>Prob.</th><th>Stake</th><th>Status</th><th>Profit</th><th></th></tr></thead>
      <tbody>
        ${data.map(e => `
          <tr>
            <td>${e.fixture}</td><td>${e.market}</td><td>${e.odd}</td><td>${e.probability}%</td><td>R$ ${e.stake}</td>
            <td>${e.result}</td><td class="${e.profit >= 0 ? 'green' : 'red'}">R$ ${e.profit}</td>
            <td>
              <button class="btn small-btn" onclick="closeEntry(${e.id},'win')">Win</button>
              <button class="btn small-btn" onclick="closeEntry(${e.id},'loss')">Loss</button>
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function closeEntry(id, result){
  await fetch("/api/close-entry", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({id, result})
  });
  loadEntries();
}

async function trainContinuous(){
  const box = document.getElementById("trainingBox");
  if(!box) return;
  const r = await fetch("/api/train-continuous");
  const t = await r.json();
  box.innerHTML = `
    <div class="card-title"><h2>Treino ${t.status}</h2><span class="pill">${t.accuracy}%</span></div>
    <h1 class="purple-text">${t.accuracy}%</h1>
    <p>Amostra: ${t.sample}</p>
    <p class="muted">${t.notes}</p>
    <br>
    <h3>Histórico de treinos</h3>
    ${t.history.map(h => `<div class="row"><span>${h.created_at}<br><small class="muted">${h.notes}</small></span><b>${h.accuracy}%</b></div>`).join("")}
  `;
}

async function sendTelegram(){
  const message = document.getElementById("telegramMsg").value;
  const r = await fetch("/api/telegram-send", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({message})
  });
  const t = await r.json();
  document.getElementById("telegramBox").innerHTML = `
    <div class="card-title"><h2>Status</h2><span class="pill">${t.status}</span></div>
    <p>${t.message}</p>
    <br><small class="muted">Para envio real, configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.</small>
  `;
}

async function loadSystemHealth(){
  const r = await fetch("/api/system-health");
  const h = await r.json();
  const box = document.getElementById("healthBox");
  if(!box) return;
  box.innerHTML = `
    <div class="card-title"><h2>Saúde do Sistema</h2><span class="pill">${h.version}</span></div>
    ${Object.entries(h).map(([k,v]) => `<div class="row"><span>${k}</span><b>${v}</b></div>`).join("")}
  `;
}

initSocket();


// =========================
// CLOUD PRO JS
// =========================
async function loadCloudHealth(){
  const box = document.getElementById("cloudHealthBox");
  if(!box) return;
  const r = await fetch("/api/cloud-health");
  const h = await r.json();
  box.innerHTML = Object.entries(h).map(([k,v]) => `
    <div class="row"><span>${k}</span><b class="pill">${v}</b></div>
  `).join("");
}

async function loadBookmakerOdds(){
  const box = document.getElementById("bookmakerOddsBox");
  if(!box) return;
  const r = await fetch("/api/bookmaker-odds");
  const data = await r.json();
  box.innerHTML = `
    <table>
      <thead><tr><th>Casa</th><th>Jogo</th><th>Mercado</th><th>Odd</th><th>Justa</th><th>Edge</th><th>Value</th></tr></thead>
      <tbody>
        ${data.map(o => `
          <tr>
            <td>${o.bookmaker}</td><td>${o.fixture}</td><td>${o.market}</td><td>${o.odd}</td>
            <td>${o.fair_odd}</td><td>${o.edge}%</td><td><span class="confidence">${o.value_score}</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function jwtLogin(){
  const email = document.getElementById("jwtEmail").value;
  const password = document.getElementById("jwtPassword").value;
  const r = await fetch("/api/jwt-login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email,password})
  });
  const data = await r.json();
  const box = document.getElementById("jwtBox");
  if(!data.ok){
    box.innerHTML = `<p class="red">${data.error}</p>`;
    return;
  }
  localStorage.setItem("sports_jwt", data.token);
  box.innerHTML = `
    <div class="card-title"><h2>Token gerado</h2><span class="pill">JWT</span></div>
    <p>Usuário: ${data.user.email}</p>
    <div class="pix-code">${data.token}</div>
    <br><small class="muted">Token salvo no navegador para uso mobile/API.</small>
  `;
}

async function trainRealML(){
  const box = document.getElementById("mlRealBox");
  if(!box) return;
  box.innerHTML = "<p class='muted'>Treinando modelo real...</p>";
  const r = await fetch("/api/ml-real-train");
  const data = await r.json();
  if(!data.ok){
    box.innerHTML = `<p class="red">${data.error}</p>`;
    return;
  }
  box.innerHTML = `
    <div class="card-title"><h2>${data.model}</h2><span class="pill">${data.accuracy}%</span></div>
    <p>Amostras: ${data.samples}</p>
    <p>Classes: ${data.classes.join(", ")}</p>
    <br>
    <div class="box">
      <b>Features usadas:</b><br><br>
      ${data.features.map(f => `<p>🧠 ${f}</p>`).join("")}
    </div>
    <br><small class="muted">${data.note}</small>
  `;
}

async function predictRealML(){
  const r = await fetch("/api/ml-real-predict", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      home_form:76,
      away_form:61,
      home_goals_avg:2.1,
      away_goals_avg:1.3,
      home_conceded_avg:0.9,
      away_conceded_avg:1.4,
      home_advantage:1
    })
  });
  const p = await r.json();
  document.getElementById("mlPredictBox").innerHTML = `
    <div class="mini-stats">
      <div><small>CASA</small><h3>${p.home_prob}%</h3></div>
      <div><small>EMPATE</small><h3>${p.draw_prob}%</h3></div>
      <div><small>FORA</small><h3>${p.away_prob}%</h3></div>
      <div><small>RESULTADO</small><h3 style="font-size:16px">${p.result}</h3></div>
    </div>
  `;
}

async function sendPushDemo(){
  const title = document.getElementById("pushTitle").value;
  const body = document.getElementById("pushBody").value;
  const r = await fetch("/api/push/send", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({title, body})
  });
  const p = await r.json();
  document.getElementById("pushBox").innerHTML = `
    <div class="card-title"><h2>${p.title}</h2><span class="pill">${p.mode}</span></div>
    <p>${p.body}</p>
    <br><small class="muted">${p.note}</small>
  `;
}


// =========================
// REAL MARKET ENGINE JS
// =========================
async function loadRealOddsPremium(){
  const box = document.getElementById("realOddsBox");
  if(!box) return;
  box.innerHTML = "<p class='muted'>Buscando odds premium...</p>";
  const r = await fetch("/api/real/odds-premium");
  const payload = await r.json();
  const data = payload.data || [];
  box.innerHTML = `
    <p class="muted">Fonte: ${payload.source} | Itens: ${payload.count}</p><br>
    <table>
      <thead><tr><th>Jogo</th><th>Casa</th><th>Mercado</th><th>Odd</th><th>Prob.</th><th>Justa</th><th>Value</th></tr></thead>
      <tbody>
        ${data.slice(0,20).map(o => `
          <tr>
            <td>${o.fixture}</td><td>${o.bookmaker}</td><td>${o.market} ${o.selection || ""}</td>
            <td>${o.odd}</td><td>${o.probability}%</td><td>${o.fair_odd}</td><td><span class="confidence">${o.value_score}</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function loadMarketRealtime(){
  const box = document.getElementById("marketRealtimeBox");
  if(!box) return;
  const r = await fetch("/api/real/market-realtime");
  const p = await r.json();
  box.innerHTML = `
    <h3>Alertas detectados</h3><br>
    ${(p.alerts || []).length ? p.alerts.map(a => `
      <div class="row">
        <span>${a.rule}<br><small class="muted">${a.fixture} | ${a.market} @ ${a.odd}</small></span>
        <b class="confidence">${a.confidence}%</b>
      </div>
    `).join("") : "<p class='muted'>Nenhum alerta premium no momento.</p>"}
  `;
}

async function runPremiumAlerts(){
  const r = await fetch("/api/real/premium-alerts-engine");
  const p = await r.json();
  alert(`${p.created} alertas premium criados.`);
  loadMarketRealtime();
  if(typeof loadAlerts === "function") loadAlerts();
}

async function runArbitrage(){
  const box = document.getElementById("arbitrageBox");
  if(!box) return;
  box.innerHTML = "<p class='muted'>Escaneando arbitragem...</p>";
  const r = await fetch("/api/real/arbitrage");
  const data = await r.json();
  if(!data.length){
    box.innerHTML = "<p class='muted'>Nenhuma arbitragem encontrada agora. Continue monitorando.</p>";
    return;
  }
  box.innerHTML = `
    <table>
      <thead><tr><th>Jogo</th><th>Mercado</th><th>Casa A</th><th>Odd A</th><th>Casa B</th><th>Odd B</th><th>Margem</th></tr></thead>
      <tbody>
        ${data.map(x => `
          <tr>
            <td>${x.fixture}</td><td>${x.market}</td><td>${x.bookmaker_a}</td><td>${x.odd_a}</td>
            <td>${x.bookmaker_b}</td><td>${x.odd_b}</td><td><span class="confidence">${x.margin}%</span></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

async function createRecurringSubscription(){
  const r = await fetch("/api/real/subscription-recurring", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({plan:"VIP PREMIUM"})
  });
  const p = await r.json();
  document.getElementById("subscriptionBox").innerHTML = `
    <div class="card-title"><h2>Assinatura</h2><span class="pill">${p.mode || "status"}</span></div>
    <p>Plano: ${p.plan || "VIP PREMIUM"}</p>
    <p>Valor: R$ ${p.amount || "79.90"}</p>
    <p>ID: ${p.subscription_id || p.message || "Aguardando produção"}</p>
  `;
}

async function runOcrOdds(){
  const text = document.getElementById("ocrText").value;
  const r = await fetch("/api/real/ocr-odds", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({text})
  });
  const p = await r.json();
  document.getElementById("ocrBox").innerHTML = `
    <div class="card-title"><h2>Odds Encontradas</h2><span class="pill">${p.count}</span></div>
    ${(p.odds_found || []).map(o => `<div class="row"><span>Odd detectada</span><b>${o}</b></div>`).join("")}
  `;
}

async function loadDeployReal(){
  const box = document.getElementById("deployRealBox");
  if(!box) return;
  const r = await fetch("/api/real/deploy-24h-guide");
  const p = await r.json();
  box.innerHTML = `
    <p>Recomendado: <b>${p.recommended}</b></p><br>
    ${p.steps.map(s => `<div class="row"><span>${s}</span><b class="pill">passo</b></div>`).join("")}
    <br><b>Variáveis:</b><br>${p.env.map(e => `<p class="muted">${e}</p>`).join("")}
  `;
}

async function loadMobileBuildGuide(){
  const box = document.getElementById("mobileBuildBox");
  if(!box) return;
  const r = await fetch("/api/real/mobile-build-guide");
  const p = await r.json();
  box.innerHTML = `
    <h3>Android</h3>${p.android.map(x => `<div class="row"><span>${x}</span></div>`).join("")}
    <br><h3>iOS</h3>${p.ios.map(x => `<div class="row"><span>${x}</span></div>`).join("")}
    <br><h3>PWA</h3>${p.pwa.map(x => `<div class="row"><span>${x}</span></div>`).join("")}
  `;
}

function toggleDetails(card){

    const details = card.querySelector(".match-details");

    if(!details) return;

    details.classList.toggle("open");
}