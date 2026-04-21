from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, db 

def register_routes(app):
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Busca o usuário no banco de dados SQLite
            user = User.query.filter_by(username=username).first()
            
            # Verifica se o usuário existe e se a senha está correta
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('home'))
                
        return render_template('login.html')

    @app.route('/')
    @login_required
    def home():
        return render_template('home.html', user=current_user)

    @app.route('/suporte')
    @login_required
    def suporte():
        return render_template('suporte.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))