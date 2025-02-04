from flask import Flask, jsonify, request
from main import app, con


@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute('SELECT id_livro, titulo, autor, ano_publicacao FROM LIVROS')
    livros2 = cur.fetchall()
    livros_dic = []
    for livro in livros2:
        livros_dic.append({
            'id_livro': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'ano_publicacao': livro[3]
        })
    return jsonify(mensagem='Lista de Livros', livros=livros_dic)


@app.route('/livro', methods=['POST'])
def livro_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM LIVROS WHERE TITULO = ?', (titulo,))

    if cursor.fetchone():
        return jsonify("Livro já cadastrado")

    cursor.execute("INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?)",
                   (titulo, autor, ano_publicacao))

    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Livro cadastrado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })

@app.route('/livro/<int:id>', methods=['PUT'])
def livro_put(id):
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    livro_data = cursor.fetchone()

    if not livro_data:
        cursor.close()
        return jsonify({"mensagem": "Livro não foi encontrado"})

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute("UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?",
                   (titulo, autor, ano_publicacao, id))
    con.commit()
    cursor.close()

    return jsonify({
        'mensagem': "Livro editado com sucesso!",
        'livro': {
            'id_livro': id,
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })