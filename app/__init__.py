from flask import Flask
from flask_login import LoginManager
from .models import db, User

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'chave_secreta_super_protegida'
    
    # Configurações do Banco de Dados SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///knowledge_base.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa os complementos no app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Tenta converter o cookie salvo para número inteiro
            return User.query.get(int(user_id))
        except ValueError:
            # Se falhar (ex: o cookie é o texto 'admin' antigo), ignora e desloga a pessoa
            return None

    # ATUALIZAÇÃO AQUI: Registrando as rotas e criando o banco
    with app.app_context():
        from .routes import register_routes
        register_routes(app) # Chama a função que gruda as rotas no app
        
        db.create_all() # Cria o arquivo knowledge_base.db automaticamente
        
        # Cria um usuário de teste se o banco estiver vazio
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='123', setor='ti')
            db.session.add(admin)
            db.session.commit()
            
        return app