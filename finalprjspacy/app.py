from flask import Flask, render_template, request
from voice_bot import run_bot

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    print("BUTTON CLICKED")
    form_url = request.form['url']
    print("Received URL:", form_url)

    run_bot(form_url)

    return "Assistant Started!"

if __name__ == "__main__":
    app.run(debug=True)