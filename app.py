from flask import Flask, render_template, request, redirect, session, url_for
import random

app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# CONFIG
# -----------------------------
HOST_PASSWORD = "admin123"

# Master clues
CLUES = [
    {"question": "I have keys but no locks. What am I?", "answer": "keyboard"},
    {"question": "What has a face and two hands but no arms?", "answer": "clock"},
    {"question": "The more you take, the more you leave behind?", "answer": "footsteps"},
    {"question": "I speak without a mouth?", "answer": "echo"},
    {"question": "What runs but never walks?", "answer": "water"},
    {"question": "I have a neck but no head?", "answer": "bottle"},
    {"question": "What gets wetter as it dries?", "answer": "towel"},
    {"question": "What has one eye but cannot see?", "answer": "needle"},
    {"question": "What has many teeth but cannot bite?", "answer": "comb"},
    {"question": "What begins with T ends with T?", "answer": "teapot"}
]

teams = {}
game_started = False


# -----------------------------
# HOME
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -----------------------------
# HOST LOGIN
# -----------------------------
@app.route('/host', methods=['GET', 'POST'])
def host():
    global game_started

    if request.method == 'POST':
        password = request.form['password']

        if password == HOST_PASSWORD:
            session['host'] = True
        else:
            return "❌ Wrong Password"

    if not session.get('host'):
        return render_template('host_login.html')

    return render_template('host.html', teams=teams, started=game_started)


# -----------------------------
# START GAME
# -----------------------------
@app.route('/start', methods=['POST'])
def start():
    global game_started

    if session.get('host'):
        game_started = True

    return redirect('/host')


# -----------------------------
# TEAM REGISTER
# -----------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        team_name = request.form['team']
        leader = request.form['leader']
        password = request.form['password']

        if team_name in teams:
            return "⚠️ Team already exists"

        clues_copy = CLUES.copy()
        random.shuffle(clues_copy)

        teams[team_name] = {
            "leader": leader,
            "password": password,
            "current": 0,
            "clues": clues_copy
        }

        return redirect('/login')

    return render_template('register.html')


# -----------------------------
# TEAM LOGIN
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        team = request.form['team']
        password = request.form['password']

        if team in teams and teams[team]['password'] == password:
            session['team'] = team
            return redirect('/team')
        else:
            return "❌ Invalid credentials"

    return render_template('login.html')


# -----------------------------
# TEAM GAME PAGE
# -----------------------------
@app.route('/team', methods=['GET', 'POST'])
def team():
    if 'team' not in session:
        return redirect('/login')

    team_name = session['team']
    team = teams[team_name]

    if not game_started:
        return "⏳ Waiting for host to start..."

    current_index = team['current']

    if current_index >= len(team['clues']):
        return "🏆 Finished!"

    clue = team['clues'][current_index]
    message = ""

    if request.method == 'POST':
        answer = request.form['answer'].lower().strip()

        if answer == clue['answer']:
            team['current'] += 1
            return redirect('/team')
        else:
            message = "❌ Wrong answer"

    return render_template('team.html',
                           clue=clue['question'],
                           progress=current_index + 1,
                           message=message)


# -----------------------------
# LEADERBOARD
# -----------------------------
@app.route('/leaderboard')
def leaderboard():
    sorted_teams = sorted(teams.items(),
                          key=lambda x: x[1]['current'],
                          reverse=True)

    return render_template('leaderboard.html', teams=sorted_teams)


# -----------------------------
# RUN
# -----------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)