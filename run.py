from app import create_app

app = create_app()

if __name__ == '__main__':
    # O host '0.0.0.0' libera o acesso para a rede local
    # A porta padrão é 5000
    app.run(host='0.0.0.0', port=5000, debug=True)