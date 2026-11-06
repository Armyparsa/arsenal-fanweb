import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask (__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
  raise RuntimeError("SECRET_KEY is not set")

DATABASE = 'database.db'


def get_db():
  conn = sqlite3.connect(DATABASE)
  conn.row_factory = sqlite3.Row
  conn.execute("PRAGMA foreign_keys = ON")
  return conn


@app.context_processor
def inject_user():
  user_id = session.get('user_id')

  if user_id is None:
    return {'current_user': None}

  conn = get_db()
  try:
    user = conn.execute('SELECT id, username, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
  finally:
    conn.close()

  return {'current_user': user}


@app.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    username = request.form.get('username', '').strip()
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')

    if not username or not password or not confirmation:
      return render_template('sign_up.html', error='Please fill in all fields.')

    if password != confirmation:
      return render_template('sign_up.html', error='Passwords do not match.')
    
    hash_password = generate_password_hash(password)
    conn = get_db()

    try:
      conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password))
      conn.commit()
    except sqlite3.IntegrityError as e:
      if "user.username" in str(e):
        return render_template('sign_up.html', error='Username already taken.')

      raise

    finally:
      conn.close()

    flash('Account created successfully. Please login.', 'success')
    return redirect(url_for('login'))
    
  return render_template('sign_up.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
      return render_template('login.html', error='Please fill both field.')

    conn = get_db()

    try:
      users = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    finally:
      conn.close()

    if users is None or not check_password_hash(users['password'], password):
      return render_template('login.html', error='Username or password is incorrect.')

    session.clear()
    session['user_id'] = users['id']
    session['is_admin'] = bool(users['is_admin'])

    flash(f"Welcome {users['username']}", 'success')
    return redirect(url_for('index'))

  return render_template('login.html')  


@app.route('/logout', methods=['POST'])
def logout():
  session.clear()
  flash('You have been logged out', 'success')
  return redirect(url_for('index'))


@app.route('/')
def index():
  conn = get_db()
  try:
    next_match = conn.execute('SELECT * FROM matches WHERE match_datetime > CURRENT_TIMESTAMP ORDER BY match_datetime ASC LIMIT 1').fetchone()
  finally:
    conn.close()
    
  return render_template('index.html', next_match=next_match)


def calculate__points(predicted_home, predicted_away, actual_home, actual_away):
  if predicted_home == actual_home and predicted_away == actual_away:
    return 5

  predicted_result = (
    1 if predicted_home > predicted_away
    else -1 if predicted_home < predicted_away
    else 0
  )

  actual_result = (
    1 if actual_home > actual_away
    else -1 if actual_home < actual_away
    else 0
  )

  if predicted_result == actual_result:
    return 3

  return 0


@app.route('/predictions', methods=["GET", "POST"])
def predictions():
  if "user_id" not in session:
    return redirect("/login")

  if request.method == "POST":
    match_id = request.form.get("match_id", type=int)
    home_score = request.form.get("home_score", type=int)
    away_score = request.form.get("away_score", type=int)

    if match_id is None or home_score is None or away_score is None:
      flash("Please Enter valid predictions")
      return redirect("/predictions")

    if home_score < 0 or away_score < 0:
      flash("Scores cannot be negative")
      return redirect("/predictions")

    db = get_db()

    try:
      match = db.execute("SELECT id, match_datetime, result_confirmed FROM matches WHERE id = ?", (match_id,)).fetchone()

      if match is None:
        flash("Match not found")
        return redirect("/predictions")

      match_time = datetime.fromisoformat(match["match_datetime"].strip())

      if match["result_confirmed"] or match_time <= datetime.now():
        flash("Predictions are closed for this match")
        return redirect(url_for("predictions"))

      db.execute("""
        INSERT INTO predictions
        (user_id, match_id, home_score, away_score)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, match_id) DO UPDATE SET
          home_score = excluded.home_score,
          away_score = excluded.away_score
        """, (
          session["user_id"],
          match_id,
          home_score,
          away_score
        ))

      db.commit()
      flash("Prediction saved successfully!")
    finally:
      db.close()

    return redirect("/predictions")

  db = get_db()

  try:
    matches = db.execute("""
        SELECT matches.*,
        predictions.home_score AS predicted_home,
        predictions.away_score AS predicted_away
        FROM matches LEFT JOIN predictions ON matches.id = predictions.match_id
        AND predictions.user_id = ? ORDER BY matches.match_datetime DESC
      """, (session["user_id"],)).fetchall()

  finally:
    db.close()

  matches = [dict(match) for match in matches]

  for match in matches:
    match["display_datetime"] = datetime.fromisoformat(
      match["match_datetime"].strip()
    ).strftime("%d %B %Y . %H:%M")


  return render_template("predictions.html", matches=matches)


@app.route('/admin/match/<int:match_id>/result', methods=['POST'])
def set_match_result(match_id):
  if "user_id" not in session:
    flash("Please login first")
    return redirect(url_for("login"))

  db = get_db()

  try:
    user = db.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if user is None or not user["is_admin"]:
      session.pop("is_admin", None)
      flash("Admin access required")
      return redirect(url_for("index"))

  finally:
    db.close()

  db = get_db()

  try:
    home_score = request.form.get("home_score", type=int)
    away_score = request.form.get("away_score", type=int)

    if (home_score is None or away_score is None or home_score < 0 or away_score < 0):
      flash("Invalid match result")
      return redirect(url_for('index'))

    match = db.execute("SELECT id FROM matches WHERE id = ?", (match_id,)).fetchone()

    if match is None:
      flash("Match not found")
      return redirect(url_for('index'))

    db.execute("""
      UPDATE matches SET home_score = ?, away_score = ?, result_confirmed = 1
      WHERE id = ?
    """, (home_score, away_score, match_id))

    predictions = db.execute("""
      SELECT id, home_score, away_score FROM predictions WHERE match_id = ?
    """, (match_id,)).fetchall()

    for prediction in predictions:
      points = calculate__points(
        prediction["home_score"],
        prediction["away_score"],
        home_score,
        away_score
      )

      db.execute("UPDATE predictions SET points = ? WHERE id = ?", (points, prediction["id"]))

    db.commit()
    flash("Match result saved and points calculated")

  finally:
    db.close()

  return redirect(url_for('index'))


@app.route('/admin/results', methods=['GET'])
def admin_results():
  if "user_id" not in session:
    flash("Please login first")
    return redirect(url_for("login"))

  db = get_db()

  try:
    user = db.execute("SELECT is_admin FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if user is None or not user["is_admin"]:
      session.pop("is_admin", None)
      flash("Admin access required")
      return redirect(url_for("index"))

    matches = db.execute("""
        SELECT id, opponent, match_datetime, competition,
              home_score, away_score, result_confirmed
        FROM matches
        ORDER BY match_datetime DESC
    """).fetchall()
  finally:
    db.close()

  return render_template('admin_result.html', matches=matches)


@app.route('/leaderboard')
def leaderboard():
  db = get_db()

  try:
    users = db.execute("""
      SELECT users.username,
      COALESCE(SUM(predictions.points), 0) AS total_points
      FROM users
      LEFT JOIN predictions ON users.id = predictions.user_id
      GROUP BY users.id
      ORDER BY total_points DESC, users.username ASC
    """).fetchall()
  finally:
    db.close()

  return render_template('leaderboard.html', users=users)


@app.route('/hall')
def hall():
  return render_template('hall_of_fame.html')


FORMATIONS = {
  "4-3-3": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("CM1", "MID"), ("CM2", "MID"), ("CM3", "MID"),
    ("LW", "FWD"), ("ST", "FWD"), ("RW", "FWD")
  ],

  "4-4-2": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("LM", "MID"), ("CM1", "MID"), ("CM2", "MID"), ("RM", "MID"),
    ("ST1", "FWD"), ("ST2", "FWD")
  ],

  "4-2-3-1": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("DM1", "MID"), ("DM2", "MID"),
    ("LAM", "FWD"), ("CAM", "MID"), ("RAM", "FWD"),
    ("ST", "FWD")
  ],

  "4-3-1-2": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("CM1", "MID"), ("CM2", "MID"), ("CM3", "MID"),
    ("CAM", "MID"),
    ("ST1", "FWD"), ("ST2", "FWD")
  ],

  "4-1-4-1": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("DM", "MID"),
    ("LM", "MID"), ("CM1", "MID"), ("CM2", "MID"), ("RM", "MID"),
    ("ST", "FWD")
  ],

  "4-2-2-2": [
    ("GK", "GK"),
    ("LB", "DEF"), ("CB1", "DEF"), ("CB2", "DEF"), ("RB", "DEF"),
    ("DM1", "MID"), ("DM2", "MID"),
    ("LAM", "MID"), ("RAM", "MID"),
    ("ST1", "FWD"), ("ST2", "FWD")
  ],

  "3-4-3": [
    ("GK", "GK"),
    ("CB1", "DEF"), ("CB2", "DEF"), ("CB3", "DEF"),
    ("LM", "MID"), ("CM1", "MID"), ("CM2", "MID"), ("RM", "MID"),
    ("LW", "FWD"), ("ST", "FWD"), ("RW", "FWD"),
  ],

  "3-5-2": [
    ("GK", "GK"),
    ("CB1", "DEF"), ("CB2", "DEF"), ("CB3", "DEF"),
    ("LM", "MID"), ("CM1", "MID"), ("CM2", "MID"), ("CM3", "MID"), ("RM", "MID"),
    ("ST1", "FWD"), ("ST2", "FWD")
  ],

  "3-4-2-1": [
    ("GK", "GK"),
    ("CB1", "DEF"), ("CB2", "DEF"), ("CB3", "DEF"),
    ("LM", "MID"), ("CM1", "MID"), ("CM2", "MID"), ("RM", "MID"),
    ("AM1", "MID"), ("AM2", "MID"),
    ("ST", "FWD")
  ],

  "5-3-2": [
    ("GK", "GK"),
    ("LWB", "DEF"), ("CB1", "DEF"), ("CB3", "DEF"),("CB2", "DEF"), ("RWB", "DEF"),
    ("CM1", "MID"), ("CM2", "MID"), ("CM3", "MID"),
    ("ST1", "FWD"), ("ST2", "FWD")
  ]
}


@app.route('/team')
def team():
  db = get_db()

  players = []
  lineup = None
  lineup_players = []

  try:
    if "user_id" in session:
      players = db.execute("""
          SELECT id, name, shirt_number, positions FROM players ORDER BY shirt_number
      """).fetchall()

      players = [dict(player) for player in players]

      lineup = db.execute("""
          SELECT id, formation FROM lineups WHERE user_id = ?
      """, (session["user_id"],)).fetchone()

      if lineup:
        lineup_players = db.execute("""
            SELECT slot, player_id FROM lineup_players WHERE lineup_id = ?
        """, (lineup["id"],)).fetchall()

        lineup_players = [dict(player) for player in lineup_players]
  finally:
    db.close()

  return render_template('current_team.html', players=players, formations=FORMATIONS, lineup=lineup, lineup_players=lineup_players)


@app.route('/save-lineup', methods=['POST'])
def save_lineup():
  if "user_id" not in session:
    return {"success": False, "message": "Login required"}, 401

  data = request.get_json()

  if not isinstance(data, dict):
    return {"success":False, "message": "Invalid data"}, 400

  formation = data.get("formation")
  selected_players = data.get("players")

  if not isinstance(formation, str) or formation not in FORMATIONS:
    return {"success": False, "message": "Invalid formation"}, 400

  if not isinstance(selected_players, dict) or len(selected_players) != 11:
    return {"success": False, "message": "You must select 11 players"}, 400

  if not all(isinstance(player_id, int) and not isinstance(player_id, bool)
             and player_id > 0 for player_id in selected_players.values()):
    return {"success": False, "message": "Invalid player IDs"}, 400

  if len(set(selected_players.values())) != 11:
    return {"success": False, "message": "A player cannot be selected twice"}, 400
  db = get_db()

  try:
    formation_slots = {
      slot: positions
      for slot, positions in FORMATIONS[formation]
    }

    if set(selected_players.keys()) != set(formation_slots.keys()):
      return {"success":False, "message": "Invalid lineup slots"}, 400

    for slot, player_id in selected_players.items():
      player = db.execute("""
          SELECT id, positions FROM players WHERE id = ?
      """, (player_id,)).fetchone()

      if player is None:
        return {"success": False, "message": "Invalid player"}, 400

      if player["positions"] != formation_slots[slot]:
        return {"success": False, "message": "Invalid player position"},400  

    lineup = db.execute("""
      SELECT id FROM lineups WHERE user_id = ?
    """, (session["user_id"],)).fetchone()

    if lineup:
      lineup_id = lineup["id"]

      db.execute("""
          UPDATE lineups SET formation = ?, updated_at = CURRENT_TIMESTAMP
          WHERE id = ?
        """, (formation,lineup_id))

      db.execute("""
          DELETE FROM lineup_players WHERE lineup_id = ?
      """, (lineup_id,))
    else:
      cursor = db.execute("""
          INSERT INTO lineups (user_id, formation) VALUES(?, ?)
      """, (session["user_id"], formation))

      lineup_id = cursor.lastrowid

    for slot, player_id in selected_players.items():
      db.execute("""
          INSERT INTO lineup_players
          (lineup_id, player_id, slot)
          VALUES (?, ?, ?)
      """, (lineup_id, player_id, slot))

    db.commit()

    return {"success": True, "message": "Line-up saved successfully"}

  except Exception:
    db.rollback()
    return {"success": False, "message": "Could not save line-up"}, 500

  finally:
    db.close()


if __name__ == '__main__':
  app.run(debug=True)