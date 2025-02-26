# Code Citations

## License: Apache_2_0
https://github.com/blabla1337/skf-flask/tree/82d270ad59e267843f70992b2bb86658fa27baf6/skf/markdown/code_examples/web/flask/16-code_example--SQL_query--.md

```
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120)
```


## License: desconhecido
https://github.com/WaleedSaleh/LiwwaSimpleHrWithS3/tree/7865e704f4bd140d680efa84ef48f80b51172a9b/backend/app.py

```
db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column
```


## License: desconhecido
https://github.com/OneOverFour/website-test/tree/5f8c64182e92758ea0268b36d9ed9890111f9b66/main.py

```
Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db
```


## License: desconhecido
https://github.com/the-mausoleum/wordpress-deploy/tree/de14184b24c0bd598dbe8bcfbe9f4a10840f2d3c/app.py

```
GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username)
```


## License: desconhecido
https://github.com/Mr-Gus/Service-Beacon/tree/a21e1dee5d3887364ccc1811b50b813c7f80943e/Service-Beacon/Service-Beacon/management-console/app.py

```
'login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request
```

