from flask import redirect, url_for
from . import create_app

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.debug=True
    app.run(debug=True)