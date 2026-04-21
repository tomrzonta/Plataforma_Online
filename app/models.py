from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Inicializa a ferramenta de banco de dados
db = SQLAlchemy()

# ==========================================
# TABELA DE USUÁRIOS
# ==========================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50)) # Ex: 'suporte', 'ti', 'rh'

# ==========================================
# TABELA DE POSTAGENS / MACROS / AVISOS
# ==========================================
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    canal = db.Column(db.String(50), nullable=False) # Ex: 'suporte-faq', 'geral'
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira ligando a postagem ao usuário que a criou
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    autor = db.relationship('User', backref=db.backref('posts', lazy=True))