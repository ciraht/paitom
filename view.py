from flask import Flask, jsonify
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