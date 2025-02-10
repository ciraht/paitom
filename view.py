from flask import Flask, jsonify, request
from main import app, con
from  flask_bcrypt import generate_password_hash, check_password_hash


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
    cursor.execute('SELECT senha FROM USUARIOS WHERE EMAIL = ?',
                   (email,))
    senha_hash = cursor.fetchone()
    senha_hash = senha_hash[0]
    if check_password_hash(senha_hash, senha):
        cursor.execute('SELECT NOME FROM USUARIOS WHERE EMAIL = ?',
                       (email,))
        nome = cursor.fetchone()
        nome = nome[0].capitalize()
        return jsonify(f'Login efetuado. Bem vindo, {nome}')
    else:
        return jsonify('Credenciais inválidas'), 401