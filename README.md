# Arsenal Fan Web

Arsenal Fan Web is a fan-made web application built as my CS50x Final Project. It gives Arsenal supporters a place to predict match scores, compare points on a leaderboard, and create their own starting XI.

## Features

- **User accounts:** Register, log in, and log out. Passwords are sorted as hashes.
- **Match predictions:** Logged-in users can submit one score prediction per match and update it until the match starts.
- **Leaderboard:** An exact score earns 5 points, a correct match outcome earns 3 points, and an incorrect outcome earns 0 points.
- **Admin results management:** Administrators can confirm match results. The application then recalculates points for every prediction on that match.
- **Lineup builder:** Logged-in users can select a formation and build a starting XI. The application validates the formation, player positions, and unique player selections before saving.
- **Arsenal news:** The homepage includes manually maintained news cards.

## Technologies

- Python
- Flask
- SQLite
- Jinja2
- HTML, CSS, and JavaScript

## Project structure

```text
arsenal-fanweb/
├── app.py
├── requirements.txt
├── schema.sql
├── seed.sql
├── .env.example
├── .gitignore
├── database.db              # generated locally; not committed
├── templates/
│   ├── admin_result.html
│   ├── base.html
│   ├── current_team.html
│   ├── hall_of_fame.html
│   ├── index.html
│   ├── leaderboard.html
│   ├── login.html
│   ├── predictions.html
│   └── sign_up.html
└── static/
    ├── css/
    ├── images/
    ├── js/
    └── styles.css
```

## Database

The database schema defines seven tables:

- `users`: usernames, hashed passwords, creation timestamps, and administrator permissions.
- `matches`: opponents, kickoff dates, competitions, stadiums, scores, and result status.
- `predictions`: each user's score prediction and points for a match. A unique constraint prevents multiple prediction rows for the same user and match.
- `players`: players available in the lineup builder.
- `lineups`: the formation saved by each user. Each user can have one saved lineup.
- `lineup_players`: the players and pitch slots assigned to a saved lineup.
- `news`: a table for news article data. The current homepage news cards are maintained directly in the template.

The database file is created locally from `schema.sql`. Match fixtures are intentionally not generated automatically; add the fixtures you want to manage to the `matches` table.

## Installation and setup

Use Python 3.10 or newer.

### 1. Clone the repository and enter the project directory

```bash
git clone https://github.com/Armyparsa/arsenal-fanweb.git
cd arsenal-fanweb
```

### 2. Create and activate a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the secret key

Copy `.env.example` to `.env`, then replace the placeholder with a randomly generated secret key.

Generate a key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Keep `.env` private. Do not commit it to GitHub.

### 5. Create and initialize the database

Run these commands from the project directory. They create the tables and insert the initial lineup-builder players:

```bash
python -c "import sqlite3; db = sqlite3.connect('database.db'); db.executescript(open('schema.sql', encoding='utf-8').read()); db.close()"
python -c "import sqlite3; db = sqlite3.connect('database.db'); db.executescript(open('seed.sql', encoding='utf-8').read()); db.close()"
```

These are manual, one-time initialization commands. The application does not recreate the tables when it starts.

### 6. Add match fixtures

No match fixtures are included in the initial seed data. Add the fixtures you want to use to the `matches` table. For example, in a SQLite client:

```sql
INSERT INTO matches
  (opponent, match_datetime, competition, stadium)
VALUES
  ('Opponent Name', 'YYYY-MM-DD HH:MM:SS', 'Competition', 'Stadium');
```

Use the server's local date and time for `match_datetime`.

### 7. Run the application

```bash
python app.py
```

Open <http://127.0.0.1:5000/> in your browser.

## Creating an administrator

1. Register a normal account through the website.
2. Stop the Flask application.
3. In SQLite, set that account's `is_admin` value to `1`:

```sql
UPDATE users
SET is_admin = 1
WHERE username = 'YOUR_USERNAME';
```

4. Restart the application and log in with that account. The Admin link will appear in the navigation bar.

## Scoring details

When an administrator confirms a match result, the application evaluates every prediction for that match:

| Prediction                                                | Points |
| --------------------------------------------------------- | -----: |
| Exact score                                               |      5 |
| Correct outcome (win, draw, or loss), but not exact score |      3 |
| Incorrect outcome                                         |      0 |

The leaderboard sums each user's points and sorts users by total points, with usernames used to break ties.

## Design decisions

I chose Flask, SQLite, Jinja2, HTML, CSS, and JavaScript because I wanted to apply the technologies and concepts I learned during CS50x in a project of my own.

The prediction and leaderboard system is intended to make following Arsenal matches more interactive. The lineup builder gives supporters the freedom to experiment with formations and choose their preferred starting XI.

## Acknowledgements

Thanks to the CS50 team for the course and its learning resources.

I also used ChatGPT as a learning and debugging assistant during development. I reviewed and adapted suggestions while building the project.
