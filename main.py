from Website import create_app
from flask_wtf.csrf import generate_csrf
from Website.models import INSTANCE_ID, EC2_AZ


app = create_app()

app.jinja_env.globals['csrf_token'] = generate_csrf
app.jinja_env.globals['iid'] = INSTANCE_ID
app.jinja_env.globals['iaz'] = EC2_AZ

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
