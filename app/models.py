from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ==========================================
# 1. USUÁRIOS E PERMISSÕES
# ==========================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(50))
    # Nível de acesso (ex: 'admin', 'editor', 'leitor') para proteger o painel
    role = db.Column(db.String(20), default='leitor') 

# ==========================================
# 2. ESTRUTURA DOS MENUS (GAVETAS DINÂMICAS)
# ==========================================
class Setor(db.Model):
    """As gavetas principais (Ex: Suporte, Marketing)"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True) # Botão Ligar/Desligar
    ordem = db.Column(db.Integer, default=0)    # Para o futuro Drag and Drop
    
    # Relação: Um setor tem várias subcategorias e notícias
    subcategorias = db.relationship('Subcategoria', backref='setor', lazy=True, cascade="all, delete-orphan")
    noticias = db.relationship('Noticia', backref='setor', lazy=True)

class Subcategoria(db.Model):
    """As sub-gavetas (Ex: Canais de atendimento, Filmagens)"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    
    # Chave Estrangeira: A qual setor esta subcategoria pertence?
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=False)
    
    # Relação: Uma subcategoria tem várias páginas (FAQs)
    paginas = db.relationship('Pagina', backref='subcategoria', lazy=True, cascade="all, delete-orphan")

# ==========================================
# 3. O CONTEÚDO (O QUE VAI DENTRO DAS GAVETAS)
# ==========================================
class Pagina(db.Model):
    """O conteúdo estático (Ex: Resposta do Reclame Aqui, Regra de Horário)"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    ordem = db.Column(db.Integer, default=0)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Para buscas filtradas e organização
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=False)

# ==========================================
# 4. NOTÍCIAS E AVISOS (PREPARAÇÃO PARA O DISCORD)
# ==========================================
class Noticia(db.Model):
    """O feed dinâmico que poderá ser disparado no Discord"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    imagem_url = db.Column(db.String(255), nullable=True) # Para imagens futuras
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Permite postar uma notícia para um setor específico (ou nulo para "Feed Geral")
    setor_id = db.Column(db.Integer, db.ForeignKey('setor.id'), nullable=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    autor = db.relationship('User', backref=db.backref('noticias', lazy=True))

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    acao = db.Column(db.String(255)) # Ex: "Criou a notícia: Bem-vindos"
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)