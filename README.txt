
# Sports Analytics Pro - Full Stack

## Como rodar no PowerShell

1. Entre na pasta:
```powershell
cd C:\Users\Rique\sports_analytics_pro_full
```

2. Instale as dependências:
```powershell
python -m pip install -r requirements.txt
```

3. Rode:
```powershell
python app.py
```

4. Abra no navegador:
```text
http://127.0.0.1:5000
```

## Login de teste

Usuário VIP:
```text
vip@sportspro.com
vip123
```

Admin:
```text
admin@sportspro.com
admin123
```

## API-Football real

Para usar jogos reais, defina sua chave no PowerShell antes de rodar:

```powershell
$env:API_FOOTBALL_KEY="SUA_CHAVE_AQUI"
python app.py
```

Sem chave, o sistema roda em modo demo premium.

## O que já vem pronto

- Site no mesmo estilo dark luxury
- Login real com sessão
- Banco SQLite
- Usuário VIP e Admin
- Jogos ao vivo reais via API-Football com fallback demo
- IA dinâmica de previsões
- Salvamento de previsões
- Painel Admin
- Gráficos reais com Chart.js
- Alertas inteligentes
- Sistema VIP / VIP PREMIUM visual
- SPA responsivo sem recarregar tela


## Atualização Elite IA Agressiva

Nesta versão, o botão "Gerar previsão IA" usa o endpoint:

/api/elite-analysis

Ele tenta buscar automaticamente na API-Football:
- ID dos times
- últimos jogos de cada time
- confronto direto H2H
- médias de gols feitos e sofridos
- BTTS
- Over 2.5
- forma recente
- risco
- mercados sugeridos
- justificativa completa

Se a chave API_FOOTBALL_KEY não estiver configurada, ele usa modo demo inteligente para continuar funcionando.


## Atualização Ultra Radar

Incluído nesta versão:
- Ultra Radar de oportunidades
- Score de valor da odd
- Odd justa calculada
- Detecção de zebra
- Heat de gols
- ML com histórico local
- Favoritos inteligentes salvos no banco
- Alertas automáticos por IA
- Ranking de risco da entrada

Rode igual antes:
python -m pip install -r requirements.txt
python app.py


## Enterprise Pack

Incluído nesta versão:
- API-Football avançada pronta para endpoints pagos
- Odds reais/value bet em estrutura pronta
- Simulador de placar
- Heatmap de pressão
- Dashboard financeiro
- Mercado Pago PIX real/demo
- Checklist de deploy
- Preparação para domínio
- Preparação para app mobile/PWA
- Procfile para deploy
- .env.example com variáveis

Para PIX real:
PowerShell:
$env:MERCADO_PAGO_TOKEN="SEU_TOKEN"
python app.py

Para API-Football real:
$env:API_FOOTBALL_KEY="SUA_CHAVE"
python app.py

Observação:
Deploy online 24h, domínio próprio e app mobile dependem de contas externas.
O código já está preparado para o próximo passo.


## Ultimate Realtime Pack

Incluído nesta versão:
- WebSocket real com Flask-SocketIO
- Feed ao vivo sem refresh
- Eventos realtime demo/plugáveis
- Stake inteligente com Kelly Criterion fracionado
- Histórico de entradas
- Fechar entradas como Win/Loss
- Treino contínuo simulado
- Telegram bot pronto para token real
- API própria documentada
- PostgreSQL-ready guide
- Deploy com Gunicorn/Eventlet
- PWA/Mobile guide

Rodar:
python -m pip install -r requirements.txt
python app.py

Variáveis opcionais:
API_FOOTBALL_KEY
MERCADO_PAGO_TOKEN
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID


## Cloud Pro Pack

Incluído nesta versão:
- JWT Auth real para API/app mobile
- PostgreSQL-ready com SQLAlchemy em cloud_models.py
- Machine Learning real com dataset CSV
- ml_train_real.py para treinar modelo
- Dataset em data/matches_dataset.csv
- Odds das casas em estrutura plugável
- Push notification preparado
- Manifest PWA + service worker
- Cloud deploy guide
- .env.example completo
- Multiusuário online preparado

Rodar:
python -m pip install -r requirements.txt
python app.py

Treinar ML real:
python ml_train_real.py

Inicializar PostgreSQL/SQLAlchemy:
python cloud_models.py


## Real Market Engine Pack

Incluído:
- API-Football odds premium real plugada em /api/real/odds-premium
- Fixtures premium em /api/real/fixtures-premium
- Análise de mercado em tempo real
- Engine de alertas premium
- Scanner de arbitragem
- OCR de odds por texto
- Assinatura recorrente Mercado Pago preparada
- IA auto-aprendizado
- Deploy 24h guide
- Mobile Android/iOS/PWA guide

Como configurar sua chave API-Football:
PowerShell:
$env:API_FOOTBALL_KEY="SUA_CHAVE_AQUI"
python app.py

Observação:
Se o endpoint /odds não estiver liberado no seu plano API-Football, o app roda em demo-premium.
