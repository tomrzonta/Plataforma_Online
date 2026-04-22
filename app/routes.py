from flask import render_template, url_for, redirect, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Noticia, Setor, Subcategoria, Pagina, Log, db 
from sqlalchemy import or_

def register_routes(app):

    # Função auxiliar para salvar logs de auditoria
    def registrar_log(mensagem):
        novo_log = Log(usuario=current_user.username, acao=mensagem)
        db.session.add(novo_log)
        db.session.commit()

# === INJEÇÃO AUTOMÁTICA PARA A BARRA LATERAL ===
    @app.context_processor
    def injetar_menus():
        # Se o usuário estiver logado, busca os setores e subcategorias do banco
        if current_user.is_authenticated:
            # Traz apenas os setores ativos, ordenados
            setores = Setor.query.filter_by(ativo=True).order_by(Setor.ordem).all()
            return dict(setores_menu=setores)
        return dict(setores_menu=[])

    # === MOTOR DE ARRASTAR E SOLTAR (DRAG AND DROP) ===
    @app.route('/admin/reordenar/<tipo>', methods=['POST'])
    @login_required
    def admin_reordenar(tipo):
        if current_user.role != 'admin': abort(403)
        
        # Recebe a nova ordem do JavaScript
        dados = request.get_json()
        nova_ordem = dados.get('ordem', [])
        
        # Identifica o que estamos reordenando
        modelo = None
        if tipo == 'setor': modelo = Setor
        elif tipo == 'subcategoria': modelo = Subcategoria
        elif tipo == 'pagina': modelo = Pagina
        
        if modelo:
            # Atualiza o banco de dados um por um na nova posição
            for index, item_id in enumerate(nova_ordem):
                item = modelo.query.get(item_id)
                if item:
                    try:
                        item.ordem = index # Salva a nova posição (0, 1, 2, 3...)
                    except Exception as e:
                        print(f"Aviso: O modelo {tipo} não tem a coluna 'ordem' configurada. Erro: {e}")
            db.session.commit()
            return jsonify({'status': 'sucesso'})
            
        return jsonify({'status': 'erro'}), 400

    # --- LOGIN E LOGOUT ---
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                return redirect(url_for('home'))
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    # --- FRONTEND: VISÃO DO USUÁRIO ---
    @app.route('/')
    @login_required
    def home():
        # O usuário só vê notícias que estão "ativas" (se você quiser ocultar alguma)
        noticias = Noticia.query.order_by(Noticia.data_criacao.desc()).all()
        # Adicionamos o user=current_user aqui no final:
        return render_template('home.html', noticias=noticias, user=current_user)
    # --- BACKEND: PAINEL ADMIN ---
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        # Trava de segurança: só admin entra aqui
        if current_user.role != 'admin':
            abort(403) # Proibido
        return render_template('admin/dashboard.html')

    @app.route('/admin/noticias', methods=['GET', 'POST'])
    @login_required
    def admin_noticias():
        if current_user.role != 'admin':
            abort(403)
            
        if request.method == 'POST':
            titulo = request.form.get('titulo')
            conteudo = request.form.get('conteudo')
            
            nova = Noticia(titulo=titulo, conteudo=conteudo, autor=current_user)
            db.session.add(nova)
            db.session.commit()
            
            registrar_log(f"Criou a notícia: {titulo}")
            return redirect(url_for('admin_noticias'))

        noticias = Noticia.query.order_by(Noticia.data_criacao.desc()).all()
        return render_template('admin/noticias.html', noticias=noticias)
    

    @app.route('/admin/noticia/deletar/<int:id>')
    @login_required
    def deletar_noticia(id):
        if current_user.role != 'admin':
            abort(403)
        noticia = Noticia.query.get_or_404(id)
        registrar_log(f"Deletou a notícia: {noticia.titulo}")
        db.session.delete(noticia)
        db.session.commit()
        return redirect(url_for('admin_noticias'))
    

    @app.route('/admin/logs')
    @login_required
    def ver_logs():
        if current_user.role != 'admin':
            abort(403)
        logs = Log.query.order_by(Log.data_hora.desc()).limit(100).all()
        return render_template('admin/logs.html', logs=logs)
    
    @app.route('/pagina/<int:id>')
    @login_required
    def ver_pagina(id):
        # Busca a página pelo ID ou retorna erro 404 se não achar
        pagina = Pagina.query.get_or_404(id)
        return render_template('pagina.html', pagina=pagina)
    
    # === ROTA DE BUSCA GLOBAL ===
    @app.route('/busca')
    @login_required
    def busca():
        # Pega a palavra que o usuário digitou na barra
        query = request.args.get('q', '')
        resultados = []
        
        if query:
            # Pesquisa ignorando maiúsculas/minúsculas (ilike) no título ou conteúdo
            resultados = Pagina.query.filter(
                or_(
                    Pagina.titulo.ilike(f'%{query}%'),
                    Pagina.conteudo.ilike(f'%{query}%')
                )
            ).all()
            
        return render_template('busca.html', query=query, resultados=resultados)
    
    # === 1. GESTÃO DE SETORES (Gavetas Principais) ===
    @app.route('/admin/setores', methods=['GET', 'POST'])
    @login_required
    def admin_setores():
        if current_user.role != 'admin': abort(403)
        if request.method == 'POST':
            nome = request.form.get('nome_setor')
            novo = Setor(nome=nome)
            db.session.add(novo)
            registrar_log(f"Criou o setor: {nome}")
            db.session.commit()
            return redirect(url_for('admin_setores'))
            
        setores = Setor.query.order_by(Setor.ordem).all()
        return render_template('admin/setores.html', setores=setores)

    # === 2. GESTÃO DE SUB-GAVETAS ===
    @app.route('/admin/conteudo', methods=['GET', 'POST'])
    @login_required
    def admin_conteudo():
        if current_user.role != 'admin': abort(403)
        if request.method == 'POST':
            nome = request.form.get('nome_subcategoria')
            setor_id = request.form.get('setor_id')
            nova_sub = Subcategoria(nome=nome, setor_id=setor_id)
            db.session.add(nova_sub)
            db.session.commit()
            registrar_log(f"Criou a sub-gaveta: {nome}")
            # Redireciona imediatamente para dentro da sub-gaveta recém criada!
            return redirect(url_for('admin_gerenciar_sub', id=nova_sub.id))
            
        setores = Setor.query.order_by(Setor.ordem).all()
        return render_template('admin/conteudo.html', setores=setores)

    # === 3. ADICIONAR MATERIAL DENTRO DA SUB-GAVETA ===
    @app.route('/admin/conteudo/<int:id>', methods=['GET', 'POST'])
    @login_required
    def admin_gerenciar_sub(id):
        if current_user.role != 'admin': abort(403)
        subcategoria = Subcategoria.query.get_or_404(id)
        
        if request.method == 'POST':
            titulo = request.form.get('titulo')
            conteudo = request.form.get('conteudo')
            nova_pagina = Pagina(titulo=titulo, conteudo=conteudo, subcategoria_id=subcategoria.id)
            db.session.add(nova_pagina)
            registrar_log(f"Adicionou material '{titulo}' na sub-gaveta '{subcategoria.nome}'")
            db.session.commit()
            return redirect(url_for('admin_gerenciar_sub', id=subcategoria.id))
            
        return render_template('admin/gerenciar_sub.html', sub=subcategoria)