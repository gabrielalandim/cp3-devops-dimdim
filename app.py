import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("POSTGRES_USER", "admin")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "senhaforte")
DB_NAME = os.environ.get("POSTGRES_DB", "dimdimdb")

def get_db_connection():
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
    return conn

# Cria a tabela automaticamente ao acessar essa rota (para facilitar os testes)
@app.route('/init', methods=['GET'])
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS contas (
            id SERIAL PRIMARY KEY,
            titular VARCHAR(100) NOT NULL,
            saldo NUMERIC(10, 2) NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Tabela criada com sucesso!"})

# CREATE
@app.route('/contas', methods=['POST'])
def create_conta():
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO contas (titular, saldo) VALUES (%s, %s) RETURNING id;',
                (data['titular'], data['saldo']))
    novo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": novo_id, "message": "Conta criada!"}), 201

# READ (Ver Todas as Contas)
@app.route('/contas', methods=['GET'])
def get_contas():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM contas;')
    contas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(contas)

# UPDATE (Atualizar Saldo)
@app.route('/contas/<int:id>', methods=['PUT'])
def update_conta(id):
    data = request.get_json()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE contas SET saldo = %s WHERE id = %s', (data['saldo'], id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Conta atualizada!"})

# DELETE (Excluir Conta)
@app.route('/contas/<int:id>', methods=['DELETE'])
def delete_conta(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM contas WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Conta deletada!"})

if __name__ == '__main__':
    # A aplicação vai rodar na porta 5000, escutando todas as interfaces
    app.run(host='0.0.0.0', port=5000)