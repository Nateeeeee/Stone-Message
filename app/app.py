from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import random
import string
import csv
import pymysql
import json
from pywebpush import webpush, WebPushException

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Nate:Natecrusader25@147.93.67.17:5432/default'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app)

VAPID_PUBLIC_KEY = "BKGeyfjwHzKcgPEM0I-XqudWHWiSVuOIFcBs5dLv5hOy9BhAaFbznVbsHqqi8zXzHcHefAMa0qpIuDVI4vAMKvI"
VAPID_PRIVATE_KEY = "LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ3hvbWtQWGk4cXJrYVZHMSsKQWhMSUNVMnlBV1NmdHVQMVl1a1NVVXlHL1BDaFJBTkNBQVNobnNuNDhCOHluSUR4RE5DUGw2cm5WaDFva2xiagppQlhBYk9YUzcrWVRzdlFZUUdoVzg1MVc3QjZxb3ZNMTh4M0IzbndER3RLcVNMZzFTT0x3RENyeQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg"
VAPID_CLAIMS = {
    "sub": "Nate:jbplsyer406@gmail.com"
}

# Modelo de Usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    registration_code = db.Column(db.String(10), nullable=True)  # Código de registro

# Modelo de Mensagem
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Cria o banco de dados e o usuário admin (execute apenas uma vez)
with app.app_context():
    db.create_all()

    # Verifica se o usuário admin já existe
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        # Cria o usuário admin
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = User(username='admin', password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print('Usuário admin criado com sucesso!')

# Função para criptografar a senha
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Função para verificar a senha
def check_password(password, hashed_password):
    if not hashed_password.startswith('$2b$'):
        return False
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Função para ler os códigos de registro do arquivo CSV
def read_registration_codes():
    codes = []
    try:
        with open('convites.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            codes = [row[0] for row in reader]
    except FileNotFoundError:
        pass
    return codes

# Função para escrever um código de registro no arquivo CSV
def write_registration_code(code):
    with open('convites.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([code])

# Função para excluir um código de registro do arquivo CSV
def delete_registration_code(code):
    codes = read_registration_codes()
    codes = [c for c in codes if c != code]
    with open('convites.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for c in codes:
            writer.writerow([c])

# Rota principal (chat)
@app.route('/')
def index():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        is_admin = user.is_admin if user else False

        # Recupera as últimas 50 mensagens do banco de dados
        messages = Message.query.order_by(Message.timestamp.desc()).limit(50).all()
        messages = list(reversed(messages))  # Ordena do mais antigo para o mais recente

        return render_template('index.html', username=session['username'], is_admin=is_admin, messages=messages)
    return redirect(url_for('login'))

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password(password, user.password):
            session['username'] = username
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        flash('Usuário ou senha inválidos', 'error')
    return render_template('login.html')

# Rota de registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        registration_code = request.form['registration_code']

        # Verifica se o código de registro é válido
        valid_codes = read_registration_codes()
        if registration_code not in valid_codes:
            flash('Código de registro inválido.', 'error')
            return redirect(url_for('register'))

        if not username or not password or not confirm_password:
            flash('Todos os campos são obrigatórios.', 'error')
        elif password != confirm_password:
            flash('As senhas não coincidem.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
        else:
            hashed_password = hash_password(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            delete_registration_code(registration_code)  # Remove o código de registro usado
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

# Rota de mudança de senha
@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        user = User.query.filter_by(username=session['username']).first()
        if not user or not check_password(current_password, user.password):
            flash('Senha atual incorreta.', 'error')
        elif new_password != confirm_password:
            flash('As novas senhas não coincidem.', 'error')
        else:
            user.password = hash_password(new_password)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('index'))
    return render_template('change_password.html')

# Rota do painel de admin
@app.route('/admin')
def admin_panel():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Verifica se o usuário é admin
    user = User.query.filter_by(username=session['username']).first()
    if not user or not user.is_admin:
        flash('Acesso negado. Você não é um administrador.', 'error')
        return redirect(url_for('index'))

    # Lista todos os usuários e códigos de registro
    users = User.query.all()
    registration_codes = read_registration_codes()
    return render_template('admin.html', users=users, registration_codes=registration_codes)

# Rota para gerar código de registro
@app.route('/admin/generate_code', methods=['POST'])
def generate_code():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Verifica se o usuário é admin
    user = User.query.filter_by(username=session['username']).first()
    if not user or not user.is_admin:
        flash('Acesso negado. Você não é um administrador.', 'error')
        return redirect(url_for('index'))

    # Gera um código de registro aleatório
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Salva o código no arquivo CSV
    write_registration_code(code)

    return redirect(url_for('admin_panel'))

# Rota para excluir código de registro
@app.route('/admin/delete_code/<string:code>', methods=['POST'])
def delete_code(code):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Verifica se o usuário é admin
    user = User.query.filter_by(username=session['username']).first()
    if not user or not user.is_admin:
        flash('Acesso negado. Você não é um administrador.', 'error')
        return redirect(url_for('index'))

    # Exclui o código do arquivo CSV
    delete_registration_code(code)

    return redirect(url_for('admin_panel'))

# Rota para editar usuário
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Verifica se o usuário é admin
    user = User.query.filter_by(username=session['username']).first()
    if not user or not user.is_admin:
        flash('Acesso negado. Você não é um administrador.', 'error')
        return redirect(url_for('index'))

    # Busca o usuário a ser editado
    user_to_edit = User.query.get_or_404(user_id)

    if request.method == 'POST':
        username = request.form['username']
        is_admin = request.form.get('is_admin') == 'on'

        user_to_edit.username = username
        user_to_edit.is_admin = is_admin
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('admin_panel'))

    return render_template('edit_user.html', user=user_to_edit)

# Rota para excluir usuário
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Verifica se o usuário é admin
    user = User.query.filter_by(username=session['username']).first()
    if not user or not user.is_admin:
        flash('Acesso negado. Você não é um administrador.', 'error')
        return redirect(url_for('index'))

    # Busca o usuário a ser excluído
    user_to_delete = User.query.get_or_404(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin_panel'))

# Rota para receber a assinatura do cliente
@app.route('/subscribe', methods=['POST'])
def subscribe():
    subscription_info = request.json
    # Armazene a assinatura no banco de dados ou em outro local
    # Aqui, apenas imprimimos para fins de demonstração
    print(subscription_info)
    return jsonify({"success": True}), 200

# SocketIO: Recebe e retransmite mensagens
@socketio.on('message')
def handleMessage(msg):
    username = session.get('username', 'Anônimo')
    
    # Salva a mensagem no banco de dados
    new_message = Message(content=msg, username=username)
    db.session.add(new_message)
    db.session.commit()

    # Envia a mensagem para todos os clientes, exceto o remetente
    send({'username': username, 'content': msg}, broadcast=True, include_self=False)

    # Envia uma notificação push para todos os clientes
    subscriptions = get_all_subscriptions()  # Função que retorna todas as assinaturas armazenadas
    for subscription in subscriptions:
        try:
            webpush(
                subscription_info=subscription,
                data=json.dumps({'username': username, 'content': msg}),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
        except WebPushException as ex:
            print("Erro ao enviar notificação push: {}", ex)

def get_all_subscriptions():
    # Função para obter todas as assinaturas armazenadas
    # Aqui, apenas retornamos uma lista vazia para fins de demonstração
    return []

if __name__ == '__main__':
    socketio.run(app,host="0.0.0.0", port=8083, debug=True, allow_unsafe_werkzeug=True)