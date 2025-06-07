from flask import Flask, g

app = Flask(__name__)

# Flag to track if startup has already run
startup_done = False

@app.before_request
def startup():
    global startup_done
    if not startup_done:
        print("This runs once before the first request")
        startup_done = True

@app.route("/")
def index():
    return "Hello, world!"

if __name__ == "__main__":
    app.run(debug=True)
