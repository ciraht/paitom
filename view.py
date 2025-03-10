from flask import Flask, jsonify, request, send_file
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
from fpdf import FPDF

import jwt

app.config.from_pyfile('config.py')
senha_secreta = app.config['SECRET_KEY']


def generate_token(user_id):
    payload = {'id_usuario': user_id}
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')
    return token

def remover_bearer(token):
    if token.startswith('Bearer '):
        return token[len('Bearer '):]
    else:
        return token

@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute('SELECT id_livro, titulo, autor, ano_publicado FROM LIVROS')
    livros2 = cur.fetchall()
    livros_dic = []
    for livro in livros2:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicado': livro[3]
        })
    return jsonify(mensagem='Lista de Livros', livros=livros_dic)


@app.route('/livro', methods=['POST'])
def livro_post():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'mensagem': 'Token de autenticação necessário'}), 401
    token = remover_bearer(token)
    try:
        payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
        id_usuario = payload['id_usuario']
    except jwt.ExpiredSignatureError:
        return jsonify({'mensagem': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'mensagem': 'Token inválido'}), 401
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicado = data.get('ano_publicado')

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE TITULO = ?', (titulo,))

    if cursor.fetchone():
        return jsonify("Livro já cadastrado")

    cursor.execute("INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICADO) VALUES (?, ?, ?)",
                   (titulo, autor, ano_publicado))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Livro cadastrado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicado': ano_publicado
        }
    })


@app.route('/livro/<int:id>', methods=['PUT'])
def livro_put(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    livro_data = cursor.fetchone()

    if not livro_data:
        cursor.close()
        return jsonify({"mensagem": "Livro não foi encontrado"})

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicado = data.get('ano_publicacao')

    cursor.execute("UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICADO = ? WHERE ID_LIVRO = ?",
                   (titulo, autor, ano_publicado, id))
    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Livro editado com sucesso!",
        'livro': {
            'id_livro': id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicado': ano_publicado
        }
    })


@app.route('/livro/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    cursor = con.cursor()

    # Verificar se o livro existe
    cursor.execute("SELECT 1 FROM livros WHERE ID_LIVRO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    # Excluir o livro
    cursor.execute("DELETE FROM livros WHERE ID_LIVRO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro excluído com sucesso!",
        'id_livro': id
    })


def validar_senha(senha):
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."

    tem_maiuscula = False
    tem_minuscula = False
    tem_numero = False
    tem_caracter_especial = False
    caracteres_especiais = "!@#$%^&*(),.?\":{}|<>"

    for char in senha:
        if char.isupper():
            tem_maiuscula = True
        elif char.islower():
            tem_minuscula = True
        elif char.isdigit():
            tem_numero = True
        elif char in caracteres_especiais:
            tem_caracter_especial = True

    if not tem_maiuscula:
        return False, "A senha deve conter pelo menos uma letra maiúscula."
    if not tem_minuscula:
        return False, "A senha deve conter pelo menos uma letra minúscula."
    if not tem_numero:
        return False, "A senha deve conter pelo menos um número."
    if not tem_caracter_especial:
        return False, "A senha deve conter pelo menos um caractere especial."

    return True, "Senha válida!"


@app.route('/usuario', methods=['POST'])
def usuario_post():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    senha_valida, mensagem_senha = validar_senha(senha)
    if not senha_valida:
        return jsonify({"erro": mensagem_senha}), 400

    senha = generate_password_hash(senha).decode('utf-8')

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM USUARIOS WHERE NOME = ?', (nome,))

    if cursor.fetchone():
        return jsonify("Usuário já cadastrado")

    cursor.execute("INSERT INTO USUARIOS(NOME, EMAIL, SENHA) VALUES (?, ?, ?)",
                   (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Usuário cadastrado com sucesso!",
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuario/<int:id>', methods=['PUT'])
def usuario_put(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({"mensagem": "Usuário não foi encontrado"})

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    # Validar a senha
    senha_valida, mensagem_senha = validar_senha(senha)
    if not senha_valida:
        return jsonify({"erro": mensagem_senha}), 400

    cursor.execute("UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?",
                   (nome, email, senha, id))
    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Usuário editado com sucesso!",
        'usuario': {
            'id_usuario': id,
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })


@app.route('/usuario/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    cursor = con.cursor()

    # Verificar se o usuario existe
    cursor.execute("SELECT 1 FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuário não encontrado"}), 404

    # Excluir o usuario
    cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuário excluído com sucesso!",
        'id_usuario': id
    })


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    cursor = con.cursor()
    cursor.execute('SELECT senha, id_usuario FROM USUARIOS WHERE EMAIL = ?', (email,))
    resultado = cursor.fetchone()
    cursor.close()

    if not resultado:
        return jsonify({"error": "Usuário não encontrado"}), 404

    id_usuario = resultado[1]
    senha_hash = resultado[0]

    if check_password_hash(senha_hash, senha):
        token = generate_token(id_usuario)
        return jsonify({'mensagem': 'Login efetuado.', 'token': token}), 200
    else:
        return jsonify('Credenciais inválidas'), 401

@app.route('/livros/relatorio', methods=['GET'])
def gerar_relatorio():
    cursor = con.cursor()
    cursor.execute("SELECT id_livro, titulo, autor, ano_publicado FROM livros")
    livros = cursor.fetchall()
    cursor.close()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "Relatorio de Livros", ln=True, align='C')
    pdf.ln(5)  # Espaço entre o título e a linha
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    for livro in livros:
        pdf.cell(200, 10, f"ID: {livro[0]} - {livro[1]} - {livro[2]} - {livro[3]}", ln=True)
    contador_livros = len(livros)
    pdf.ln(10)  # Espaço antes do contador
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, f"Total de livros cadastrados: {contador_livros}", ln=True, align='C')
    pdf_path = "relatorio_livros.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True, mimetype='application/pdf')