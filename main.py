from Website import create_app
from flask_wtf.csrf import generate_csrf


app = create_app()

app.jinja_env.globals['csrf_token'] = generate_csrf

if __name__ == '__main__':
    app.run(debug=True)