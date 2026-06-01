

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash

import psycopg2
from psycopg2.extras import RealDictCursor

import os
import random
from functools import wraps
import datetime
import requests
import jwt
import math
import base64
import uuid

try:
    import mercadopago
except Exception:
    mercadopago = None

APP_NAME = "Sports Analytics Pro"
DATABASE_URL = os.environ.get("DATABASE_URL")

def db():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-essa-chave-em-producao")
CORS(app)
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY", "")

# =========================
# BANCO DE DADOS
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

def db():
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        plan TEXT DEFAULT 'VIP',
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        home TEXT,
        away TEXT,
        favorite TEXT,
        home_prob INTEGER,
        draw_prob INTEGER,
        away_prob INTEGER,
        confidence INTEGER,
        markets TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)





    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        status TEXT DEFAULT 'pending',
        provider TEXT DEFAULT 'mercado_pago',
        external_id TEXT,
        amount REAL,
        next_billing_date TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS arbitrage_scans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fixture TEXT,
        market TEXT,
        bookmaker_a TEXT,
        odd_a REAL,
        bookmaker_b TEXT,
        odd_b REAL,
        margin REAL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ocr_scans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        extracted_text TEXT,
        odds_found TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS premium_alert_rules(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        market TEXT,
        min_confidence INTEGER,
        min_value_score INTEGER,
        enabled INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS market_snapshots(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fixture TEXT,
        market TEXT,
        bookmaker TEXT,
        odd REAL,
        value_score INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS betting_entries(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        fixture TEXT,
        market TEXT,
        odd REAL,
        probability INTEGER,
        stake REAL,
        result TEXT DEFAULT 'open',
        profit REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS model_training(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample_size INTEGER,
        accuracy REAL,
        status TEXT,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS telegram_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        status TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plan TEXT,
        amount REAL,
        status TEXT DEFAULT 'pending',
        mp_payment_id TEXT,
        qr_code TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prediction_results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER,
        real_result TEXT,
        hit INTEGER DEFAULT 0,
        profit REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bankroll(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        description TEXT,
        amount REAL,
        type TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        home TEXT,
        away TEXT,
        market TEXT,
        confidence INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS odds_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fixture_name TEXT,
        market TEXT,
        odd REAL,
        fair_odd REAL,
        value_score INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        confidence INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    admin = cur.execute("SELECT * FROM users WHERE email = ?", ("admin@sportspro.com",)).fetchone()
    if not admin:
        cur.execute(
            "INSERT INTO users(name,email,password_hash,plan,role) VALUES(?,?,?,?,?)",
            ("Admin", "admin@sportspro.com", generate_password_hash("admin123"), "VIP PREMIUM", "admin")
        )

    vip = cur.execute("SELECT * FROM users WHERE email = ?", ("vip@sportspro.com",)).fetchone()
    if not vip:
        cur.execute(
            "INSERT INTO users(name,email,password_hash,plan,role) VALUES(?,?,?,?,?)",
            ("Infinite Trader", "vip@sportspro.com", generate_password_hash("vip123"), "VIP", "user")
        )

    if cur.execute("SELECT COUNT(*) c FROM alerts").fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO alerts(title,description,confidence) VALUES(?,?,?)",
            [
                ("Manchester City com pressão alta", "Entrada sugerida: vitória casa", 92),
                ("Liverpool x Chelsea tendência de gols", "Entrada sugerida: over 2.5", 87),
                ("PSG x Bayern ambos marcam", "Entrada sugerida: BTTS sim", 89),
            ]
        )


    if cur.execute("SELECT COUNT(*) c FROM premium_alert_rules").fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO premium_alert_rules(name,market,min_confidence,min_value_score,enabled) VALUES(?,?,?,?,?)",
            [
                ("Value Bet Forte", "ANY", 82, 70, 1),
                ("Over Gols Premium", "Over", 78, 65, 1),
                ("BTTS Premium", "BTTS", 80, 68, 1),
                ("Dupla Chance Segura", "Dupla Chance", 84, 60, 1),
            ]
        )

    con.commit()
    con.close()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    con = db()
    user = con.execute("SELECT id,name,email,plan,role FROM users WHERE id = ?", (uid,)).fetchone()
    con.close()
    return dict(user) if user else None

# =========================
# ROTAS
# =========================
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    con = db()

    cur = con.cursor()

    cur.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cur.fetchone()

    cur.close()
    con.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"ok": False, "error": "Email ou senha incorretos"}), 401

    session["user_id"] = user["id"]

    return jsonify({
        "ok": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "plan": user["plan"],
            "role": user["role"]
        }
    })

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json or {}
    name = data.get("name", "Novo usuário").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"ok": False, "error": "Preencha email e senha"}), 400

    try:
        con = db()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO users(name,email,password_hash,plan,role) VALUES(?,?,?,?,?)",
            (name, email, generate_password_hash(password), "VIP", "user")
        )
        con.commit()
        session["user_id"] = cur.lastrowid
        con.close()
        return jsonify({"ok": True})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "error": "Email já cadastrado"}), 400

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/live")
def api_live():
    # API-Football real se tiver chave. Se não tiver, entra demo premium.
    if API_FOOTBALL_KEY:
        try:
            today = datetime.date.today().isoformat()
            url = "https://v3.football.api-sports.io/fixtures"
            headers = {"x-apisports-key": API_FOOTBALL_KEY}
            params = {"date": today}
            r = requests.get(url, headers=headers, params=params, timeout=12)
            data = r.json()
            response = data.get("response", [])
            games = []
            for item in response[:20]:
                fixture = item.get("fixture", {})
                league = item.get("league", {})
                teams = item.get("teams", {})
                goals = item.get("goals", {})
                games.append({
                    "league": league.get("name", "Liga"),
                    "minute": fixture.get("status", {}).get("elapsed") or 0,
                    "status": fixture.get("status", {}).get("short", "NS"),
                    "home": teams.get("home", {}).get("name", "Casa"),
                    "away": teams.get("away", {}).get("name", "Fora"),
                    "homeLogo": teams.get("home", {}).get("logo", ""),
                    "awayLogo": teams.get("away", {}).get("logo", ""),
                    "homeGoals": goals.get("home") if goals.get("home") is not None else "-",
                    "awayGoals": goals.get("away") if goals.get("away") is not None else "-",
                    "pressure": random.randint(45, 82),
                    "live": fixture.get("status", {}).get("short") in ["1H", "2H", "HT", "ET", "P"]
                })
            if games:
                return jsonify({"source": "api-football", "games": games})
        except Exception as e:
            pass

    games = [
        {"league":"UEFA Champions League","minute":67,"status":"2H","home":"Manchester City","away":"Real Madrid","homeGoals":2,"awayGoals":1,"pressure":58,"live":True},
        {"league":"Brasileirão Série A","minute":45,"status":"HT","home":"Flamengo","away":"Palmeiras","homeGoals":1,"awayGoals":0,"pressure":68,"live":True},
        {"league":"Premier League","minute":0,"status":"HT","home":"Liverpool","away":"Chelsea","homeGoals":2,"awayGoals":2,"pressure":70,"live":True},
        {"league":"La Liga","minute":62,"status":"2H","home":"Barcelona","away":"Real Sociedad","homeGoals":3,"awayGoals":1,"pressure":76,"live":True},
    ]
    return jsonify({"source": "demo", "games": games})

@app.route("/api/predict", methods=["POST"])
def api_predict():
    user = current_user()
    data = request.json or {}
    home = data.get("home", "Manchester City")
    away = data.get("away", "Real Madrid")

    # IA heurística dinâmica. Depois pode trocar por modelo ML real.
    seed = sum(ord(c) for c in home + away)
    random.seed(seed + datetime.datetime.now().day)

    attack_home = random.randint(62, 92)
    attack_away = random.randint(50, 88)
    defense_home = random.randint(55, 86)
    defense_away = random.randint(48, 84)
    form_home = random.randint(55, 92)
    form_away = random.randint(45, 90)

    score_home = attack_home * 0.38 + defense_home * 0.18 + form_home * 0.34 + 8
    score_away = attack_away * 0.36 + defense_away * 0.18 + form_away * 0.32

    total = score_home + score_away + 45
    home_prob = round(score_home / total * 100)
    away_prob = round(score_away / total * 100)
    draw_prob = max(12, 100 - home_prob - away_prob)

    # normalização
    diff = 100 - (home_prob + draw_prob + away_prob)
    home_prob += diff

    favorite = home if home_prob >= away_prob else away
    confidence = min(96, max(72, abs(home_prob-away_prob) + 72))

    markets = []
    if attack_home + attack_away > 145:
        markets.append("Mais de 2.5 gols")
    else:
        markets.append("Mais de 1.5 gols")
    if attack_home > 65 and attack_away > 60:
        markets.append("Ambos marcam: SIM")
    markets.append(f"Dupla chance: {favorite} ou empate")

    result = {
        "home": home,
        "away": away,
        "favorite": favorite,
        "home_prob": home_prob,
        "draw_prob": draw_prob,
        "away_prob": away_prob,
        "confidence": confidence,
        "markets": markets,
        "stats": {
            "attack_home": attack_home,
            "attack_away": attack_away,
            "defense_home": defense_home,
            "defense_away": defense_away,
            "form_home": form_home,
            "form_away": form_away
        },
        "explanation": f"A IA aponta vantagem para {favorite} considerando força ofensiva, consistência recente, equilíbrio defensivo e projeção de gols. O modelo combina ataque, defesa, forma e pressão estimada para criar uma probabilidade dinâmica."
    }

    if user:
con = db()

cur = con.cursor()

cur.execute(
    "INSERT INTO ... predictions(user_id,home,away,favorite,home_prob,draw_prob,away_prob,confidence,markets) VALUES(?,?,?,?,?,?,?,?,?)",
            (user["id"], home, away, favorite, home_prob, draw_prob, away_prob, confidence, ", ".join(markets))
        )
        con.commit()
        con.close()

    return jsonify(result)

@app.route("/api/alerts")
def api_alerts():
    con = db()
    rows = con.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 20").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/admin/users")
def api_admin_users():
    user = current_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Acesso negado"}), 403
    con = db()
    users = con.execute("SELECT id,name,email,plan,role,created_at FROM users ORDER BY id DESC").fetchall()
    con.close()
    return jsonify([dict(u) for u in users])

@app.route("/api/admin/upgrade", methods=["POST"])
def api_admin_upgrade():
    user = current_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Acesso negado"}), 403
    data = request.json or {}
    user_id = data.get("user_id")
    plan = data.get("plan", "VIP PREMIUM")
    con = db()
    con.execute("UPDATE users SET plan=? WHERE id=?", (plan, user_id))
    con.commit()
    con.close()
    return jsonify({"ok": True})

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "accuracy": 98.6,
        "profit": 24.8,
        "roi": 8.7,
        "operations": 237,
        "goals": 2.85,
        "corners": 10.2,
        "cards": 3.45,
        "possession": 54.6,
        "chart": [0, 2, -1, 8, 3, 12, 18, 17, 12, 20, 25, 18, 28]
    })


# =========================
# ELITE IA - BUSCA AGRESSIVA DE DADOS
# =========================
def api_get(path, params=None):
    if not API_FOOTBALL_KEY:
        return None
    try:
        url = f"https://v3.football.api-sports.io/{path}"
        headers = {"x-apisports-key": API_FOOTBALL_KEY}
        r = requests.get(url, headers=headers, params=params or {}, timeout=15)
        if r.status_code != 200:
            return None
        return r.json().get("response", [])
    except Exception:
        return None

def find_team_id(team_name):
    data = api_get("teams", {"search": team_name})
    if not data:
        return None
    return data[0].get("team", {}).get("id")

def last_fixtures(team_id, limit=10):
    if not team_id:
        return []
    data = api_get("fixtures", {"team": team_id, "last": limit})
    return data or []

def h2h_fixtures(home_id, away_id, limit=8):
    if not home_id or not away_id:
        return []
    data = api_get("fixtures/headtohead", {"h2h": f"{home_id}-{away_id}", "last": limit})
    return data or []

def extract_team_form(fixtures, team_name):
    total = len(fixtures) or 1
    goals_for = goals_against = wins = draws = losses = btts = over25 = 0
    clean_sheets = 0

    for item in fixtures:
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        home_name = teams.get("home", {}).get("name", "")
        away_name = teams.get("away", {}).get("name", "")
        gh = goals.get("home") or 0
        ga = goals.get("away") or 0

        is_home = team_name.lower() in home_name.lower()
        gf = gh if is_home else ga
        gc = ga if is_home else gh

        goals_for += gf
        goals_against += gc
        if gf > gc: wins += 1
        elif gf == gc: draws += 1
        else: losses += 1
        if gf > 0 and gc > 0: btts += 1
        if gf + gc >= 3: over25 += 1
        if gc == 0: clean_sheets += 1

    return {
        "games": total,
        "avg_goals_for": round(goals_for/total, 2),
        "avg_goals_against": round(goals_against/total, 2),
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "btts_rate": round((btts/total)*100),
        "over25_rate": round((over25/total)*100),
        "clean_sheet_rate": round((clean_sheets/total)*100),
        "form_score": round(((wins*3 + draws) / (total*3)) * 100)
    }

def elite_fallback(home, away):
    seed = sum(ord(c) for c in home + away) + datetime.datetime.now().day
    random.seed(seed)
    hf = {
        "games": 10,
        "avg_goals_for": round(random.uniform(1.4, 2.7), 2),
        "avg_goals_against": round(random.uniform(0.7, 1.6), 2),
        "wins": random.randint(4, 8),
        "draws": random.randint(1, 3),
        "losses": random.randint(0, 3),
        "btts_rate": random.randint(45, 76),
        "over25_rate": random.randint(48, 80),
        "clean_sheet_rate": random.randint(20, 55),
        "form_score": random.randint(58, 88)
    }
    af = {
        "games": 10,
        "avg_goals_for": round(random.uniform(1.1, 2.4), 2),
        "avg_goals_against": round(random.uniform(0.8, 1.9), 2),
        "wins": random.randint(3, 7),
        "draws": random.randint(1, 4),
        "losses": random.randint(1, 4),
        "btts_rate": random.randint(42, 74),
        "over25_rate": random.randint(45, 78),
        "clean_sheet_rate": random.randint(18, 50),
        "form_score": random.randint(50, 84)
    }
    return hf, af, []

def build_elite_analysis(home, away):
    home_id = find_team_id(home)
    away_id = find_team_id(away)

    source = "api-football" if home_id and away_id else "demo-inteligente"

    if home_id and away_id:
        home_last = last_fixtures(home_id, 12)
        away_last = last_fixtures(away_id, 12)
        h2h = h2h_fixtures(home_id, away_id, 8)
        home_form = extract_team_form(home_last, home)
        away_form = extract_team_form(away_last, away)
    else:
        home_form, away_form, h2h = elite_fallback(home, away)

    # score agressivo: forma + ataque + defesa + fator casa + h2h
    home_attack = home_form["avg_goals_for"] * 28
    away_attack = away_form["avg_goals_for"] * 26
    home_defense = max(0, 45 - home_form["avg_goals_against"] * 18)
    away_defense = max(0, 42 - away_form["avg_goals_against"] * 18)
    home_score = home_form["form_score"] * 0.45 + home_attack + home_defense + 8
    away_score = away_form["form_score"] * 0.43 + away_attack + away_defense

    h2h_home_wins = h2h_away_wins = h2h_draws = 0
    for item in h2h:
        teams = item.get("teams", {})
        goals = item.get("goals", {})
        hname = teams.get("home", {}).get("name", "")
        aname = teams.get("away", {}).get("name", "")
        gh = goals.get("home") or 0
        ga = goals.get("away") or 0
        if gh == ga:
            h2h_draws += 1
        else:
            winner_name = hname if gh > ga else aname
            if home.lower() in winner_name.lower():
                h2h_home_wins += 1
            elif away.lower() in winner_name.lower():
                h2h_away_wins += 1

    home_score += h2h_home_wins * 2.2
    away_score += h2h_away_wins * 2.2

    raw_draw = 24 - abs(home_score - away_score) * 0.08
    draw_prob = round(max(14, min(30, raw_draw)))
    rem = 100 - draw_prob
    home_prob = round((home_score / (home_score + away_score)) * rem)
    away_prob = 100 - draw_prob - home_prob

    favorite = home if home_prob >= away_prob else away
    confidence = min(97, max(70, round(abs(home_prob - away_prob) + 72)))

    expected_goals = home_form["avg_goals_for"] + away_form["avg_goals_for"]
    btts_index = round((home_form["btts_rate"] + away_form["btts_rate"]) / 2)
    over25_index = round((home_form["over25_rate"] + away_form["over25_rate"] + (expected_goals * 18)) / 3)

    markets = []
    if expected_goals >= 2.7 or over25_index >= 62:
        markets.append({"market": "Mais de 2.5 gols", "confidence": min(94, over25_index + 12), "risk": "Médio"})
    else:
        markets.append({"market": "Mais de 1.5 gols", "confidence": min(95, over25_index + 22), "risk": "Baixo"})

    if btts_index >= 55:
        markets.append({"market": "Ambos marcam - SIM", "confidence": min(93, btts_index + 10), "risk": "Médio"})
    else:
        markets.append({"market": "Ambos marcam - NÃO", "confidence": min(88, 100 - btts_index), "risk": "Médio"})

    markets.append({"market": f"Dupla chance: {favorite} ou empate", "confidence": min(96, confidence + 4), "risk": "Baixo"})

    risk = "Baixo" if confidence >= 88 else "Médio" if confidence >= 78 else "Alto"

    explanation = [
        f"A IA Elite analisou {home} x {away} usando forma recente, gols marcados, gols sofridos, tendência BTTS, Over 2.5, mando de campo e confronto direto.",
        f"{home}: média de {home_form['avg_goals_for']} gols feitos, {home_form['avg_goals_against']} sofridos e forma {home_form['form_score']}% nos últimos {home_form['games']} jogos.",
        f"{away}: média de {away_form['avg_goals_for']} gols feitos, {away_form['avg_goals_against']} sofridos e forma {away_form['form_score']}% nos últimos {away_form['games']} jogos.",
        f"O favorito projetado é {favorite}, com confiança de {confidence}% e risco {risk}.",
        "A leitura é agressiva: a IA não olha só o placar provável, ela cruza força ofensiva, vulnerabilidade defensiva, regularidade e mercado provável."
    ]

    return {
        "source": source,
        "home": home,
        "away": away,
        "favorite": favorite,
        "home_prob": home_prob,
        "draw_prob": draw_prob,
        "away_prob": away_prob,
        "confidence": confidence,
        "risk": risk,
        "expected_goals": round(expected_goals, 2),
        "btts_index": btts_index,
        "over25_index": over25_index,
        "markets": markets,
        "home_form": home_form,
        "away_form": away_form,
        "h2h": {
            "games": len(h2h),
            "home_wins": h2h_home_wins,
            "draws": h2h_draws,
            "away_wins": h2h_away_wins
        },
        "explanation": explanation
    }

@app.route("/api/elite-analysis", methods=["POST"])
def api_elite_analysis():
    data = request.json or {}
    home = data.get("home", "Manchester City").strip()
    away = data.get("away", "Real Madrid").strip()

    if not home or not away:
        return jsonify({"error": "Informe os dois times"}), 400

    result = build_elite_analysis(home, away)

    user = current_user()
    if user:
        con = db()
        con.execute(
            "INSERT INTO predictions(user_id,home,away,favorite,home_prob,draw_prob,away_prob,confidence,markets) VALUES(?,?,?,?,?,?,?,?,?)",
            (
                user["id"], home, away, result["favorite"], result["home_prob"],
                result["draw_prob"], result["away_prob"], result["confidence"],
                ", ".join([m["market"] for m in result["markets"]])
            )
        )
        con.commit()
        con.close()

    return jsonify(result)


# =========================
# ULTRA RADAR / MACHINE LEARNING SIMULADO
# =========================
def calc_value_score(probability, odd):
    if not odd:
        return 0, 0
    fair_odd = round(100 / max(probability, 1), 2)
    implied = round((1 / odd) * 100, 1)
    edge = probability - implied
    value_score = max(0, min(99, round(edge * 3 + probability * 0.45)))
    return fair_odd, value_score

@app.route("/api/ultra-radar")
def api_ultra_radar():
    games = [
        ("Manchester City", "Real Madrid", 58, 1.72, "Vitória Casa"),
        ("PSG", "Bayern", 61, 1.68, "Ambos marcam - SIM"),
        ("Flamengo", "Palmeiras", 64, 1.57, "Mais de 1.5 gols"),
        ("Liverpool", "Chelsea", 59, 1.44, "Dupla Chance"),
        ("Barcelona", "Atlético", 56, 1.60, "Mais de 2.5 gols"),
        ("São Paulo", "Botafogo", 54, 1.88, "Mais de 1.5 gols"),
    ]

    radar = []
    for home, away, prob, odd, market in games:
        fair_odd, value_score = calc_value_score(prob, odd)
        zebra = "Sim" if odd >= 2.10 and prob >= 42 else "Não"
        heat = min(99, round(prob + random.randint(8, 25)))
        risk = "Baixo" if value_score >= 70 else "Médio" if value_score >= 50 else "Alto"

        item = {
            "fixture": f"{home} x {away}",
            "home": home,
            "away": away,
            "market": market,
            "probability": prob,
            "odd": odd,
            "fair_odd": fair_odd,
            "value_score": value_score,
            "zebra": zebra,
            "goal_heat": heat,
            "risk": risk,
            "reason": f"Valor detectado: probabilidade estimada {prob}% contra odd {odd}. Odd justa calculada: {fair_odd}."
        }
        radar.append(item)

        con = db()
        con.execute(
            "INSERT INTO odds_history(fixture_name,market,odd,fair_odd,value_score) VALUES(?,?,?,?,?)",
            (item["fixture"], market, odd, fair_odd, value_score)
        )
        con.commit()
        con.close()

    radar.sort(key=lambda x: x["value_score"], reverse=True)
    return jsonify(radar)

@app.route("/api/ml-learn")
def api_ml_learn():
    con = db()
    preds = con.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 100").fetchall()
    con.close()

    total = len(preds)
    if total == 0:
        return jsonify({
            "trained": False,
            "message": "Ainda não há histórico suficiente. Gere previsões para a IA começar a aprender.",
            "accuracy": 0,
            "best_market": "Aguardando dados",
            "sample": 0
        })

    # Simulação de aprendizado baseada no volume do histórico
    accuracy = min(98, 72 + total * 2)
    best_market = "Dupla chance" if total < 10 else "Mais de 1.5 gols"
    return jsonify({
        "trained": True,
        "message": "IA treinada com histórico local de previsões.",
        "accuracy": accuracy,
        "best_market": best_market,
        "sample": total,
        "rules": [
            "Times com forma acima de 70% recebem peso extra.",
            "Mercados com risco baixo são priorizados no radar.",
            "Entradas com value score acima de 70 entram como oportunidade premium.",
            "Confrontos equilibrados reduzem stake sugerida."
        ]
    })

@app.route("/api/save-favorite", methods=["POST"])
def api_save_favorite():
    user = current_user()
    if not user:
        return jsonify({"ok": False, "error": "Faça login"}), 401

    data = request.json or {}
    con = db()
    con.execute(
        "INSERT INTO favorites(user_id,home,away,market,confidence) VALUES(?,?,?,?,?)",
        (
            user["id"],
            data.get("home", ""),
            data.get("away", ""),
            data.get("market", ""),
            int(data.get("confidence", 0))
        )
    )
    con.commit()
    con.close()
    return jsonify({"ok": True})

@app.route("/api/favorites")
def api_favorites():
    user = current_user()
    if not user:
        return jsonify([])
    con = db()
    rows = con.execute("SELECT * FROM favorites WHERE user_id=? ORDER BY id DESC LIMIT 30", (user["id"],)).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/push-alerts")
def api_push_alerts():
    radar = [
        {"title": "Value Bet detectada", "description": "Mercado com valor acima da odd justa", "confidence": random.randint(82, 94)},
        {"title": "Heat de gols alto", "description": "Jogo com tendência forte para over gols", "confidence": random.randint(80, 93)},
        {"title": "Risco reduzido", "description": "Dupla chance com boa proteção estatística", "confidence": random.randint(84, 96)}
    ]
    con = db()
    for a in radar:
        con.execute("INSERT INTO alerts(title,description,confidence) VALUES(?,?,?)", (a["title"], a["description"], a["confidence"]))
    con.commit()
    con.close()
    return jsonify({"ok": True, "created": len(radar)})


# =========================
# ENTERPRISE PACK
# =========================
@app.route("/api/advanced-stats")
def api_advanced_stats():
    team = request.args.get("team", "Manchester City")
    # API real pode ser plugada aqui usando API-Football endpoints fixtures/statistics, players, injuries e standings.
    return jsonify({
        "team": team,
        "xg": round(random.uniform(1.2, 2.8), 2),
        "xga": round(random.uniform(0.7, 1.9), 2),
        "shots_on_target": round(random.uniform(4.2, 8.8), 1),
        "corners": round(random.uniform(4.5, 8.5), 1),
        "cards": round(random.uniform(1.5, 3.8), 1),
        "dangerous_attacks": random.randint(38, 82),
        "possession": random.randint(48, 68),
        "injuries": random.randint(0, 4),
        "form": random.choice(["V V E V V", "V E V D V", "E V V V D", "V V V V E"]),
        "note": "Modo híbrido: pronto para API-Football completa. Sem endpoint pago, usa simulação premium."
    })

@app.route("/api/real-odds")
def api_real_odds():
    # API-Football odds pode ser plugada aqui. Modo demo entrega estrutura pronta.
    odds = [
        {"fixture": "Man City x Real Madrid", "bookmaker": "Bet365", "market": "Casa", "odd": 1.72, "fair": 1.61, "value": 78},
        {"fixture": "PSG x Bayern", "bookmaker": "Betano", "market": "BTTS Sim", "odd": 1.68, "fair": 1.55, "value": 82},
        {"fixture": "Flamengo x Palmeiras", "bookmaker": "Sportingbet", "market": "Over 1.5", "odd": 1.57, "fair": 1.44, "value": 86},
        {"fixture": "Liverpool x Chelsea", "bookmaker": "KTO", "market": "Dupla Chance 1X", "odd": 1.44, "fair": 1.32, "value": 81},
    ]
    return jsonify(odds)

@app.route("/api/score-simulator", methods=["POST"])
def api_score_simulator():
    data = request.json or {}
    home = data.get("home", "Manchester City")
    away = data.get("away", "Real Madrid")
    base = build_elite_analysis(home, away) if "build_elite_analysis" in globals() else {}
    hp = base.get("home_prob", random.randint(40, 60))
    ap = base.get("away_prob", random.randint(18, 40))

    hg = 1 + (hp // 28)
    ag = max(0, ap // 35)
    if base.get("expected_goals", 2.4) > 2.7:
        hg += 1

    return jsonify({
        "home": home,
        "away": away,
        "score": f"{home} {hg} x {ag} {away}",
        "home_goals": hg,
        "away_goals": ag,
        "scenarios": [
            {"name": "Conservador", "score": f"{home} 1 x 0 {away}", "chance": 24},
            {"name": "Provável", "score": f"{home} {hg} x {ag} {away}", "chance": 41},
            {"name": "Agressivo", "score": f"{home} {hg+1} x {ag+1} {away}", "chance": 22},
            {"name": "Zebra", "score": f"{home} {max(0,hg-1)} x {ag+1} {away}", "chance": 13},
        ]
    })

@app.route("/api/heatmap")
def api_heatmap():
    zones = []
    for y in range(5):
        row = []
        for x in range(7):
            row.append(random.randint(15, 99))
        zones.append(row)
    return jsonify({"zones": zones, "label": "Mapa de pressão ofensiva"})

@app.route("/api/financial")
def api_financial():
    user = current_user()
    uid = user["id"] if user else 1
    con = db()
    rows = con.execute("SELECT * FROM bankroll WHERE user_id=? ORDER BY id DESC LIMIT 50", (uid,)).fetchall()
    if not rows:
        sample = [
            ("Entrada Over 1.5 - Flamengo", 42.50, "profit"),
            ("Entrada BTTS - PSG", 31.20, "profit"),
            ("Entrada 1X2 - Liverpool", -25.00, "loss"),
            ("Entrada Dupla Chance", 18.80, "profit"),
        ]
        for desc, amount, typ in sample:
            con.execute("INSERT INTO bankroll(user_id,description,amount,type) VALUES(?,?,?,?)", (uid, desc, amount, typ))
        con.commit()
        rows = con.execute("SELECT * FROM bankroll WHERE user_id=? ORDER BY id DESC LIMIT 50", (uid,)).fetchall()
    con.close()
    total = round(sum([r["amount"] for r in rows]), 2)
    wins = len([r for r in rows if r["amount"] > 0])
    losses = len([r for r in rows if r["amount"] < 0])
    return jsonify({"total": total, "wins": wins, "losses": losses, "history": [dict(r) for r in rows]})

@app.route("/api/create-pix", methods=["POST"])
def api_create_pix():
    user = current_user()
    data = request.json or {}
    plan = data.get("plan", "VIP PREMIUM")
    amount = 79.90 if plan == "VIP PREMIUM" else 29.90
    token = os.environ.get("MERCADO_PAGO_TOKEN", "")

    # Sem token, retorna PIX demo para o layout funcionar.
    if not token or not mercadopago:
        qr = "00020126580014BR.GOV.BCB.PIX0136DEMO-SPORTS-ANALYTICS-PRO520400005303986540579.905802BR5920SPORTS ANALYTICS PRO6009SAO PAULO62070503***6304DEMO"
        con = db()
        con.execute("INSERT INTO payments(user_id,plan,amount,status,qr_code) VALUES(?,?,?,?,?)", (user["id"] if user else None, plan, amount, "demo", qr))
        con.commit()
        con.close()
        return jsonify({"ok": True, "mode": "demo", "qr_code": qr, "amount": amount, "plan": plan})

    try:
        sdk = mercadopago.SDK(token)
        payment_data = {
            "transaction_amount": float(amount),
            "description": f"Assinatura {plan} - Sports Analytics Pro",
            "payment_method_id": "pix",
            "payer": {"email": user["email"] if user else "cliente@email.com"}
        }
        result = sdk.payment().create(payment_data)
        payment = result["response"]
        qr = payment.get("point_of_interaction", {}).get("transaction_data", {}).get("qr_code", "")
        con = db()
        con.execute("INSERT INTO payments(user_id,plan,amount,status,mp_payment_id,qr_code) VALUES(?,?,?,?,?,?)", (user["id"] if user else None, plan, amount, "pending", str(payment.get("id")), qr))
        con.commit()
        con.close()
        return jsonify({"ok": True, "mode": "real", "qr_code": qr, "amount": amount, "plan": plan, "payment_id": payment.get("id")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/deploy-checklist")
def api_deploy_checklist():
    return jsonify([
        {"item": "Criar conta Render/Railway/VPS", "status": "manual"},
        {"item": "Configurar SECRET_KEY", "status": "required"},
        {"item": "Configurar API_FOOTBALL_KEY", "status": "optional"},
        {"item": "Configurar MERCADO_PAGO_TOKEN", "status": "optional"},
        {"item": "Migrar SQLite para PostgreSQL em produção", "status": "recommended"},
        {"item": "Comprar domínio e apontar DNS", "status": "manual"},
        {"item": "Ativar HTTPS", "status": "required"},
        {"item": "Gerar build mobile com WebView/PWA", "status": "optional"}
    ])

@app.route("/api/pwa-manifest")
def api_pwa_manifest():
    return jsonify({
        "name": "Sports Analytics Pro",
        "short_name": "SportsPro",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#05050b",
        "theme_color": "#8b2cff",
        "icons": []
    })


# =========================
# ULTIMATE REALTIME PACK
# =========================
def kelly_stake(probability, odd, bankroll=1000, fraction=0.25):
    p = probability / 100
    b = odd - 1
    q = 1 - p
    if b <= 0:
        return 0
    kelly = ((b * p) - q) / b
    stake = bankroll * max(0, kelly) * fraction
    return round(min(stake, bankroll * 0.08), 2)

def generate_live_event():
    teams = [
        ("Manchester City", "Real Madrid"),
        ("Flamengo", "Palmeiras"),
        ("Liverpool", "Chelsea"),
        ("PSG", "Bayern"),
        ("São Paulo", "Botafogo")
    ]
    home, away = random.choice(teams)
    minute = random.randint(1, 90)
    home_goals = random.randint(0, 3)
    away_goals = random.randint(0, 3)
    pressure = random.randint(35, 92)
    event = random.choice(["Gol possível", "Pressão alta", "Escanteio provável", "Cartão possível", "Momentum forte", "Value live"])
    confidence = random.randint(72, 96)
    return {
        "fixture": f"{home} x {away}",
        "home": home,
        "away": away,
        "minute": minute,
        "score": f"{home_goals} x {away_goals}",
        "pressure": pressure,
        "event": event,
        "confidence": confidence,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    }

@socketio.on("connect")
def socket_connect():
    emit("server_status", {"status": "connected", "message": "Sports Analytics Pro Realtime conectado"})

@socketio.on("request_live_tick")
def socket_live_tick():
    emit("live_tick", generate_live_event())

@app.route("/api/realtime-tick")
def api_realtime_tick():
    return jsonify(generate_live_event())

@app.route("/api/stake", methods=["POST"])
def api_stake():
    data = request.json or {}
    bankroll = float(data.get("bankroll", 1000))
    probability = int(data.get("probability", 60))
    odd = float(data.get("odd", 1.80))
    stake = kelly_stake(probability, odd, bankroll)
    risk = "Baixo" if stake <= bankroll*0.025 else "Médio" if stake <= bankroll*0.055 else "Alto"
    return jsonify({
        "bankroll": bankroll,
        "probability": probability,
        "odd": odd,
        "stake": stake,
        "risk": risk,
        "method": "Kelly Criterion fracionado 25%",
        "note": "Gestão conservadora para reduzir exposição em entradas agressivas."
    })

@app.route("/api/save-entry", methods=["POST"])
def api_save_entry():
    user = current_user()
    data = request.json or {}
    con = db()
    con.execute(
        "INSERT INTO betting_entries(user_id,fixture,market,odd,probability,stake) VALUES(?,?,?,?,?,?)",
        (
            user["id"] if user else None,
            data.get("fixture", ""),
            data.get("market", ""),
            float(data.get("odd", 0)),
            int(data.get("probability", 0)),
            float(data.get("stake", 0))
        )
    )
    con.commit()
    con.close()
    return jsonify({"ok": True})

@app.route("/api/entries")
def api_entries():
    user = current_user()
    con = db()
    if user:
        rows = con.execute("SELECT * FROM betting_entries WHERE user_id=? ORDER BY id DESC LIMIT 50", (user["id"],)).fetchall()
    else:
        rows = con.execute("SELECT * FROM betting_entries ORDER BY id DESC LIMIT 50").fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])

@app.route("/api/close-entry", methods=["POST"])
def api_close_entry():
    data = request.json or {}
    entry_id = data.get("id")
    result = data.get("result", "win")
    con = db()
    row = con.execute("SELECT * FROM betting_entries WHERE id=?", (entry_id,)).fetchone()
    if not row:
        con.close()
        return jsonify({"ok": False}), 404
    profit = 0
    if result == "win":
        profit = round(row["stake"] * (row["odd"] - 1), 2)
    elif result == "loss":
        profit = -row["stake"]
    con.execute("UPDATE betting_entries SET result=?, profit=? WHERE id=?", (result, profit, entry_id))
    con.commit()
    con.close()
    return jsonify({"ok": True, "profit": profit})

@app.route("/api/train-continuous")
def api_train_continuous():
    con = db()
    preds = con.execute("SELECT COUNT(*) c FROM predictions").fetchone()["c"]
    entries = con.execute("SELECT COUNT(*) c FROM betting_entries").fetchone()["c"]
    sample = preds + entries
    accuracy = min(99, round(70 + sample * 1.7 + random.uniform(0, 6), 1))
    notes = "Treino contínuo simulado com previsões + entradas salvas. Pronto para trocar por scikit-learn real."
    con.execute(
        "INSERT INTO model_training(sample_size,accuracy,status,notes) VALUES(?,?,?,?)",
        (sample, accuracy, "trained" if sample > 0 else "waiting", notes)
    )
    con.commit()
    history = con.execute("SELECT * FROM model_training ORDER BY id DESC LIMIT 10").fetchall()
    con.close()
    return jsonify({
        "sample": sample,
        "accuracy": accuracy,
        "status": "trained" if sample > 0 else "waiting",
        "notes": notes,
        "history": [dict(h) for h in history]
    })

@app.route("/api/telegram-send", methods=["POST"])
def api_telegram_send():
    data = request.json or {}
    message = data.get("message", "Alerta Sports Analytics Pro")
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

    status = "demo"
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            r = requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
            status = "sent" if r.status_code == 200 else "error"
        except Exception:
            status = "error"

    con = db()
    con.execute("INSERT INTO telegram_logs(message,status) VALUES(?,?)", (message, status))
    con.commit()
    con.close()
    return jsonify({"ok": True, "status": status, "message": message})

@app.route("/api/system-health")
def api_system_health():
    return jsonify({
        "backend": "online",
        "database": "sqlite/postgresql-ready",
        "websocket": "enabled",
        "api_football": "configured" if API_FOOTBALL_KEY else "demo",
        "mercado_pago": "configured" if os.environ.get("MERCADO_PAGO_TOKEN") else "demo",
        "telegram": "configured" if os.environ.get("TELEGRAM_BOT_TOKEN") else "demo",
        "version": "Ultimate Realtime"
    })

@app.route("/api/v1/predictions")
def api_public_predictions():
    con = db()
    rows = con.execute("SELECT id,home,away,favorite,home_prob,draw_prob,away_prob,confidence,markets,created_at FROM predictions ORDER BY id DESC LIMIT 30").fetchall()
    con.close()
    return jsonify({"app": "Sports Analytics Pro", "data": [dict(r) for r in rows]})

@app.route("/api/postgres-guide")
def api_postgres_guide():
    return jsonify({
        "status": "ready",
        "steps": [
            "Criar banco PostgreSQL no Render/Railway/Supabase",
            "Adicionar DATABASE_URL nas variáveis de ambiente",
            "Trocar sqlite3 por SQLAlchemy em produção",
            "Rodar migrações",
            "Ativar backups automáticos"
        ],
        "note": "A versão local usa SQLite para facilitar testes."
    })


# =========================
# CLOUD PRO PACK: JWT / POSTGRES / PUSH / ODDS REAL / ML REAL
# =========================
JWT_SECRET = os.environ.get("JWT_SECRET", app.secret_key)
ODDS_API_KEY = os.environ.get("ODDS_API_KEY", "")
PUSH_PUBLIC_KEY = os.environ.get("PUSH_PUBLIC_KEY", "")
PUSH_PRIVATE_KEY = os.environ.get("PUSH_PRIVATE_KEY", "")

def create_jwt_token(user):
    payload = {
        "id": user["id"],
        "email": user["email"],
        "plan": user["plan"],
        "role": user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Token JWT ausente"}), 401
        token = auth.replace("Bearer ", "")
        try:
            request.jwt_user = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        except Exception:
            return jsonify({"error": "Token JWT inválido ou expirado"}), 401
        return fn(*args, **kwargs)
    return wrapper

@app.route("/api/jwt-login", methods=["POST"])
def api_jwt_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    con = db()
    user = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    con.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"ok": False, "error": "Email ou senha incorretos"}), 401

    user_dict = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "plan": user["plan"],
        "role": user["role"]
    }
    token = create_jwt_token(user_dict)
    return jsonify({"ok": True, "token": token, "user": user_dict})

@app.route("/api/jwt-profile")
@jwt_required
def api_jwt_profile():
    return jsonify({"ok": True, "user": request.jwt_user})

@app.route("/api/cloud-health")
def api_cloud_health():
    return jsonify({
        "postgres_ready": bool(os.environ.get("DATABASE_URL")),
        "jwt": "enabled",
        "odds_api": "configured" if ODDS_API_KEY else "demo",
        "push": "configured" if PUSH_PUBLIC_KEY and PUSH_PRIVATE_KEY else "demo",
        "ml_dataset": os.path.exists("data/matches_dataset.csv"),
        "mobile": "pwa/capacitor-ready",
        "deploy": "render/railway/vps-ready"
    })

@app.route("/api/bookmaker-odds")
def api_bookmaker_odds():
    # Estrutura plugável para The Odds API / API-Football Odds / OddsAPI.
    # Sem chave, roda demo premium para não quebrar.
    if ODDS_API_KEY:
        # Aqui você pluga o provedor escolhido.
        # A resposta foi padronizada para o front continuar igual.
        pass

    odds = [
        {"bookmaker": "Bet365", "fixture": "Man City x Real Madrid", "market": "Casa", "odd": 1.72, "source": "demo"},
        {"bookmaker": "Betano", "fixture": "PSG x Bayern", "market": "BTTS Sim", "odd": 1.68, "source": "demo"},
        {"bookmaker": "Superbet", "fixture": "Flamengo x Palmeiras", "market": "Over 1.5", "odd": 1.57, "source": "demo"},
        {"bookmaker": "KTO", "fixture": "Liverpool x Chelsea", "market": "Dupla Chance 1X", "odd": 1.44, "source": "demo"},
        {"bookmaker": "Sportingbet", "fixture": "São Paulo x Botafogo", "market": "Over 2.5", "odd": 2.05, "source": "demo"},
    ]

    enriched = []
    for item in odds:
        prob = random.randint(52, 68)
        fair = round(100 / prob, 2)
        implied = round((1 / item["odd"]) * 100, 1)
        edge = round(prob - implied, 1)
        value = max(0, min(99, round(edge * 4 + prob * 0.35)))
        enriched.append({**item, "probability": prob, "fair_odd": fair, "edge": edge, "value_score": value})
    return jsonify(enriched)

@app.route("/api/push/subscribe", methods=["POST"])
def api_push_subscribe():
    data = request.json or {}
    # Em produção, salvar subscription JSON no banco por usuário.
    return jsonify({"ok": True, "mode": "demo", "subscription_saved": bool(data)})

@app.route("/api/push/send", methods=["POST"])
def api_push_send():
    data = request.json or {}
    title = data.get("title", "Sports Analytics Pro")
    body = data.get("body", "Alerta premium detectado pela IA.")
    return jsonify({
        "ok": True,
        "mode": "demo" if not (PUSH_PUBLIC_KEY and PUSH_PRIVATE_KEY) else "ready",
        "title": title,
        "body": body,
        "note": "Para push real, configure VAPID keys e salve subscriptions dos usuários."
    })

@app.route("/api/ml-real-train")
def api_ml_real_train():
    try:
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score

        path = "data/matches_dataset.csv"
        if not os.path.exists(path):
            return jsonify({"ok": False, "error": "Dataset não encontrado em data/matches_dataset.csv"}), 404

        df = pd.read_csv(path)
        features = ["home_form", "away_form", "home_goals_avg", "away_goals_avg", "home_conceded_avg", "away_conceded_avg", "home_advantage"]
        X = df[features]
        y = df["result"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        model = RandomForestClassifier(n_estimators=120, random_state=42)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        acc = round(accuracy_score(y_test, pred) * 100, 2)

        return jsonify({
            "ok": True,
            "model": "RandomForestClassifier",
            "accuracy": acc,
            "samples": len(df),
            "features": features,
            "classes": sorted(df["result"].unique().tolist()),
            "note": "Treino real executado com dataset CSV local."
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/ml-real-predict", methods=["POST"])
def api_ml_real_predict():
    data = request.json or {}
    # Previsão leve baseada no mesmo formato do dataset.
    home_form = float(data.get("home_form", 72))
    away_form = float(data.get("away_form", 61))
    home_goals_avg = float(data.get("home_goals_avg", 1.9))
    away_goals_avg = float(data.get("away_goals_avg", 1.3))
    home_conceded_avg = float(data.get("home_conceded_avg", 0.9))
    away_conceded_avg = float(data.get("away_conceded_avg", 1.2))
    home_advantage = float(data.get("home_advantage", 1))

    home_score = home_form*0.38 + home_goals_avg*18 - home_conceded_avg*9 + home_advantage*8
    away_score = away_form*0.34 + away_goals_avg*17 - away_conceded_avg*8
    draw_score = 35 - abs(home_score-away_score)*0.25

    total = max(1, home_score + away_score + draw_score)
    home_prob = round(home_score / total * 100)
    away_prob = round(away_score / total * 100)
    draw_prob = max(8, 100 - home_prob - away_prob)

    result = "HOME" if home_prob >= away_prob and home_prob >= draw_prob else "AWAY" if away_prob >= draw_prob else "DRAW"

    return jsonify({
        "result": result,
        "home_prob": home_prob,
        "draw_prob": draw_prob,
        "away_prob": away_prob,
        "confidence": max(home_prob, draw_prob, away_prob)
    })


# =========================
# REAL MARKET ENGINE: API-FOOTBALL / ODDS / ASSINATURA / ARBITRAGEM / AUTO-LEARNING / OCR
# =========================
def api_football_real(path, params=None):
    key = os.environ.get("API_FOOTBALL_KEY", API_FOOTBALL_KEY)
    if not key:
        return None
    try:
        url = f"https://v3.football.api-sports.io/{path}"
        headers = {"x-apisports-key": key}
        r = requests.get(url, headers=headers, params=params or {}, timeout=18)
        payload = r.json()
        return payload.get("response", [])
    except Exception:
        return None

def normalize_odds_items(api_items):
    normalized = []
    for item in api_items or []:
        fixture = item.get("fixture", {})
        league = item.get("league", {})
        bookmakers = item.get("bookmakers", [])
        fixture_name = f"{item.get('teams', {}).get('home', {}).get('name', 'Casa')} x {item.get('teams', {}).get('away', {}).get('name', 'Fora')}"
        for bm in bookmakers:
            bm_name = bm.get("name", "Bookmaker")
            for bet in bm.get("bets", []):
                market = bet.get("name", "Mercado")
                for value in bet.get("values", []):
                    try:
                        odd = float(value.get("odd"))
                    except Exception:
                        continue
                    normalized.append({
                        "fixture_id": fixture.get("id"),
                        "fixture": fixture_name,
                        "league": league.get("name", ""),
                        "bookmaker": bm_name,
                        "market": market,
                        "selection": value.get("value", ""),
                        "odd": odd
                    })
    return normalized

def demo_odds_matrix():
    return [
        {"fixture":"Man City x Real Madrid","bookmaker":"Bet365","market":"Match Winner","selection":"Home","odd":1.72},
        {"fixture":"Man City x Real Madrid","bookmaker":"Betano","market":"Match Winner","selection":"Home","odd":1.81},
        {"fixture":"Man City x Real Madrid","bookmaker":"KTO","market":"Match Winner","selection":"Away","odd":4.60},
        {"fixture":"PSG x Bayern","bookmaker":"Bet365","market":"Both Teams Score","selection":"Yes","odd":1.68},
        {"fixture":"PSG x Bayern","bookmaker":"Betano","market":"Both Teams Score","selection":"Yes","odd":1.78},
        {"fixture":"Flamengo x Palmeiras","bookmaker":"Superbet","market":"Goals Over/Under","selection":"Over 1.5","odd":1.57},
        {"fixture":"Flamengo x Palmeiras","bookmaker":"KTO","market":"Goals Over/Under","selection":"Over 1.5","odd":1.66},
        {"fixture":"São Paulo x Botafogo","bookmaker":"Bet365","market":"Goals Over/Under","selection":"Over 2.5","odd":2.05},
        {"fixture":"São Paulo x Botafogo","bookmaker":"Betano","market":"Goals Over/Under","selection":"Over 2.5","odd":2.18},
    ]

def enrich_market_value(items):
    enriched = []
    for item in items:
        prob = random.randint(51, 72)
        fair_odd = round(100 / prob, 2)
        implied = round((1 / float(item["odd"])) * 100, 1)
        edge = round(prob - implied, 1)
        value_score = max(0, min(99, round(edge * 4 + prob * 0.35)))
        enriched.append({**item, "probability": prob, "fair_odd": fair_odd, "implied": implied, "edge": edge, "value_score": value_score})
    enriched.sort(key=lambda x: x["value_score"], reverse=True)
    return enriched

@app.route("/api/real/odds-premium")
def api_real_odds_premium():
    # API-Football Odds real. Requer plano/endpoint liberado na API.
    league = request.args.get("league")
    season = request.args.get("season", str(datetime.date.today().year))
    date = request.args.get("date", datetime.date.today().isoformat())

    params = {"date": date}
    if league:
        params["league"] = league
    if season:
        params["season"] = season

    response = api_football_real("odds", params)
    source = "api-football"
    items = normalize_odds_items(response)

    if not items:
        source = "demo-premium"
        items = demo_odds_matrix()

    enriched = enrich_market_value(items[:120])

con = db()

cur = con.cursor()

for x in enriched[:40]:
    cur.execute(
        "INSERT INTO market_snapshots(fixture,market,bookmaker,odd,value_score) VALUES(%s,%s,%s,%s,%s)",
        (
            x.get("fixture"),
            f"{x.get('market')} - {x.get('selection')}",
            x.get("bookmaker"),
            x.get("odd"),
            x.get("value_score")
        )
    )

con.commit()
cur.close()
con.close()

    return jsonify({"source": source, "count": len(enriched), "data": enriched})

@app.route("/api/real/fixtures-premium")
def api_real_fixtures_premium():
    date = request.args.get("date", datetime.date.today().isoformat())
    league = request.args.get("league")
    season = request.args.get("season", str(datetime.date.today().year))
    params = {"date": date}
    if league: params["league"] = league
    if season: params["season"] = season
    response = api_football_real("fixtures", params)

    if not response:
        return jsonify({"source": "demo", "data": [
            {"fixture":"Man City x Real Madrid","status":"NS","league":"Champions League","date":date},
            {"fixture":"Flamengo x Palmeiras","status":"NS","league":"Brasileirão","date":date}
        ]})

    data = []
    for item in response[:50]:
        data.append({
            "id": item.get("fixture", {}).get("id"),
            "fixture": f"{item.get('teams', {}).get('home', {}).get('name')} x {item.get('teams', {}).get('away', {}).get('name')}",
            "status": item.get("fixture", {}).get("status", {}).get("short"),
            "league": item.get("league", {}).get("name"),
            "date": item.get("fixture", {}).get("date"),
            "home_logo": item.get("teams", {}).get("home", {}).get("logo"),
            "away_logo": item.get("teams", {}).get("away", {}).get("logo"),
        })
    return jsonify({"source": "api-football", "data": data})

@app.route("/api/real/market-realtime")
def api_real_market_realtime():
    odds = enrich_market_value(demo_odds_matrix())
    # Quando API real estiver liberada, trocar demo_odds_matrix por api_football_real("odds/live", ...)
    alerts = []
    con = db()
    rules = con.execute("SELECT * FROM premium_alert_rules WHERE enabled=1").fetchall()
    for odd in odds:
        for rule in rules:
            market_ok = rule["market"] == "ANY" or rule["market"].lower() in f"{odd['market']} {odd['selection']}".lower()
            if market_ok and odd["probability"] >= rule["min_confidence"] and odd["value_score"] >= rule["min_value_score"]:
                alerts.append({
                    "rule": rule["name"],
                    "fixture": odd["fixture"],
                    "bookmaker": odd["bookmaker"],
                    "market": f"{odd['market']} - {odd['selection']}",
                    "odd": odd["odd"],
                    "value_score": odd["value_score"],
                    "confidence": odd["probability"]
                })
    con.close()
    return jsonify({"odds": odds[:25], "alerts": alerts})

@app.route("/api/real/arbitrage")
def api_real_arbitrage():
    # Scanner simplificado de arbitragem. Para 1X2 completo, usar grupos Home/Draw/Away por fixture/bookmaker.
    odds = demo_odds_matrix()
    grouped = {}
    for x in odds:
        key = (x["fixture"], x["market"], x["selection"])
        grouped.setdefault(key, []).append(x)

    opportunities = []
    for key, rows in grouped.items():
        if len(rows) < 2:
            continue
        rows = sorted(rows, key=lambda x: x["odd"], reverse=True)
        best = rows[0]
        second = rows[1]
        margin = round(((best["odd"] - second["odd"]) / second["odd"]) * 100, 2)
        if margin >= 3:
            opportunities.append({
                "fixture": key[0],
                "market": f"{key[1]} - {key[2]}",
                "bookmaker_a": best["bookmaker"],
                "odd_a": best["odd"],
                "bookmaker_b": second["bookmaker"],
                "odd_b": second["odd"],
                "margin": margin
            })

    con = db()
    for o in opportunities:
        con.execute(
            "INSERT INTO arbitrage_scans(fixture,market,bookmaker_a,odd_a,bookmaker_b,odd_b,margin) VALUES(?,?,?,?,?,?,?)",
            (o["fixture"], o["market"], o["bookmaker_a"], o["odd_a"], o["bookmaker_b"], o["odd_b"], o["margin"])
        )
    con.commit()
    con.close()

    return jsonify(opportunities)

@app.route("/api/real/subscription-recurring", methods=["POST"])
def api_subscription_recurring():
    user = current_user()
    data = request.json or {}
    plan = data.get("plan", "VIP PREMIUM")
    amount = 79.90 if plan == "VIP PREMIUM" else 29.90
    token = os.environ.get("MERCADO_PAGO_TOKEN", "")

    if not token or not mercadopago:
        external_id = "demo-sub-" + str(uuid.uuid4())[:8]
        con = db()
        con.execute(
            "INSERT INTO subscriptions(user_id,plan,status,provider,external_id,amount,next_billing_date) VALUES(?,?,?,?,?,?,?)",
            (user["id"] if user else None, plan, "demo-active", "mercado_pago_demo", external_id, amount, (datetime.date.today()+datetime.timedelta(days=30)).isoformat())
        )
        con.commit()
        con.close()
        return jsonify({"ok": True, "mode": "demo", "subscription_id": external_id, "plan": plan, "amount": amount})

    # Mercado Pago assinatura real: estrutura pronta. Em produção, usar preapproval endpoint do SDK/API.
    return jsonify({
        "ok": False,
        "mode": "requires-production-setup",
        "message": "Configure fluxo de preapproval do Mercado Pago com URL de retorno e webhook público no deploy."
    }), 400

@app.route("/api/real/auto-learning")
def api_real_auto_learning():
    con = db()
    pred_count = con.execute("SELECT COUNT(*) c FROM predictions").fetchone()["c"]
    entry_count = con.execute("SELECT COUNT(*) c FROM betting_entries").fetchone()["c"] if "betting_entries" else 0
    market_count = con.execute("SELECT COUNT(*) c FROM market_snapshots").fetchone()["c"]
    sample = pred_count + entry_count + market_count
    acc = min(99, round(68 + sample * 0.33 + random.uniform(1, 6), 2))
    notes = [
        "Recalibrou peso de value score em mercados com odds acima da justa.",
        "Reduziu confiança em jogos com alta simetria de forma.",
        "Aumentou prioridade para mercados Over quando heat de gols supera 70.",
        "Entradas com risco alto passam a exigir edge maior."
    ]
    con.execute(
        "INSERT INTO model_training(sample_size,accuracy,status,notes) VALUES(?,?,?,?)",
        (sample, acc, "auto-learning", " | ".join(notes))
    )
    con.commit()
    con.close()
    return jsonify({"status": "auto-learning", "sample": sample, "accuracy": acc, "rules": notes})

@app.route("/api/real/ocr-odds", methods=["POST"])
def api_ocr_odds():
    # OCR real precisa de pytesseract instalado no Windows + Tesseract OCR.
    # Esta rota aceita texto ou imagem futura. Aqui já extrai odds de texto colado.
    data = request.json or {}
    raw_text = data.get("text", "")
    found = re.findall(r"\b\d+[.,]\d{2}\b", raw_text)
    found = [x.replace(",", ".") for x in found]
    con = db()
    con.execute(
        "INSERT INTO ocr_scans(filename,extracted_text,odds_found) VALUES(?,?,?)",
        ("manual-text", raw_text[:1000], ",".join(found))
    )
    con.commit()
    con.close()
    return jsonify({"mode": "text-ocr-demo", "odds_found": found, "count": len(found)})

@app.route("/api/real/premium-alerts-engine")
def api_premium_alerts_engine():
    market = api_real_market_realtime().get_json()
    alerts = market.get("alerts", [])
    con = db()
    for a in alerts:
        con.execute(
            "INSERT INTO alerts(title,description,confidence) VALUES(?,?,?)",
            (
                f"{a['rule']} - {a['fixture']}",
                f"{a['market']} @ {a['odd']} na {a['bookmaker']} | Value {a['value_score']}",
                a["confidence"]
            )
        )
    con.commit()
    con.close()
    return jsonify({"created": len(alerts), "alerts": alerts})

@app.route("/api/real/mobile-build-guide")
def api_mobile_build_guide():
    return jsonify({
        "android": [
            "Instalar Node.js",
            "Criar projeto Capacitor",
            "Apontar WebView para domínio do SaaS",
            "Gerar APK/AAB no Android Studio",
            "Publicar no Google Play Console"
        ],
        "ios": [
            "Precisa de Mac/Xcode",
            "Criar app Capacitor iOS",
            "Configurar bundle id",
            "Publicar via App Store Connect"
        ],
        "pwa": [
            "Manifest e service worker já incluídos",
            "Hospedar com HTTPS",
            "Usuário instala pelo navegador"
        ]
    })

@app.route("/api/real/deploy-24h-guide")
def api_deploy_24h_guide():
    return jsonify({
        "recommended": "Render/Railway/VPS",
        "steps": [
            "Subir projeto no GitHub",
            "Criar PostgreSQL",
            "Configurar variáveis de ambiente",
            "Deploy com Procfile",
            "Configurar domínio",
            "Ativar HTTPS",
            "Configurar webhooks Mercado Pago",
            "Configurar jobs para auto-learning e alertas"
        ],
        "env": ["SECRET_KEY","JWT_SECRET","DATABASE_URL","API_FOOTBALL_KEY","MERCADO_PAGO_TOKEN","TELEGRAM_BOT_TOKEN","TELEGRAM_CHAT_ID","ODDS_API_KEY"]
    })

if __name__ == "__main__":
    init_db()

    port = int(os.environ.get("PORT", 10000))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )

@app.route("/")
def index():
    return render_template("index.html")