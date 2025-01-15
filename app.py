from flask import Flask, jsonify, render_template, request, send_from_directory
import sqlite3
import json
import os

app = Flask(__name__, static_folder='static')

# Configuração do banco de dados
DATABASE = 'arretado_burger.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        
        # Criar tabelas
        db.execute('''
        CREATE TABLE IF NOT EXISTS burgers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            imagem TEXT
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS combos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            imagem TEXT
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            preco REAL NOT NULL,
            categoria TEXT NOT NULL,
            imagem TEXT
        )
        ''')
        
        db.execute('''
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            endereco TEXT NOT NULL,
            telefone TEXT NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pendente',
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Inserir dados iniciais
        burgers = [
            ('X-ARRETADO', 'Pão grande, 2x Carnes, 2x Queijo, Presunto, Ovo, Calabresa, Bacon, Milho, Batata Palha, Creme de Requeijão e Salada', 16.00, 'burgers/x-arretado.jpg'),
            ('X-BAITA BURGÃO', 'Pão grande, Carne, Queijo, Presunto, Ovo, Calabresa, Bacon, Milho, Batata Palha, Creme de Requeijão e Salada', 13.00, 'burgers/x-baita.jpg'),
            ('X-TUDO', 'Pão grande, Carne, Queijo, Presunto, Ovo, Calabresa, Bacon, Milho, Batata Palha e Salada', 12.00, 'burgers/x-tudo.jpg'),
            ('X-EGG', 'Pão grande, Carne, Queijo, Ovo e Salada', 10.00, 'burgers/x-egg.jpg'),
            ('X-BACON', 'Pão grande, Carne, Queijo, Bacon e Salada', 10.00, 'burgers/x-bacon.jpg'),
            ('X-BURGUER', 'Pão grande, Carne, Queijo e Salada', 8.00, 'burgers/x-burguer.jpg')
        ]
        
        combos = [
            ('COMBO ARRETADO', '2 X-ARRETADO + GUARANÁ 1L', 40.00, 'combos/combo-arretado.jpg'),
            ('COMBO FAMÍLIA', '2 X-TUDO + COCA-COLA 2L', 35.00, 'combos/combo-familia.jpg'),
            ('COMBO INDIVIDUAL', '1 X-BURGUER + REFRIGERANTE LATA', 12.00, 'combos/combo-individual.jpg')
        ]
        
        produtos = [
            ('BATATA FRITA P', 'Porção de batata frita pequena', 8.00, 'petisco', 'produtos/batata-frita-p.jpg'),
            ('BATATA FRITA M', 'Porção de batata frita média', 12.00, 'petisco', 'produtos/batata-frita-m.jpg'),
            ('BATATA FRITA G', 'Porção de batata frita grande', 15.00, 'petisco', 'produtos/batata-frita-g.jpg'),
            ('COCA-COLA 2L', 'Refrigerante Coca-Cola 2 litros', 12.00, 'bebida', 'produtos/coca-2l.jpg'),
            ('GUARANÁ 1L', 'Refrigerante Guaraná Antarctica 1 litro', 8.00, 'bebida', 'produtos/guarana-1l.jpg'),
            ('REFRIGERANTE LATA', 'Refrigerante em lata 350ml', 5.00, 'bebida', 'produtos/refri-lata.jpg'),
            ('ÁGUA MINERAL', 'Água mineral sem gás 500ml', 3.00, 'bebida', 'produtos/agua.jpg')
        ]
        
        db.executemany('INSERT OR IGNORE INTO burgers (nome, descricao, preco, imagem) VALUES (?, ?, ?, ?)', burgers)
        db.executemany('INSERT OR IGNORE INTO combos (nome, descricao, preco, imagem) VALUES (?, ?, ?, ?)', combos)
        db.executemany('INSERT OR IGNORE INTO produtos (nome, descricao, preco, categoria, imagem) VALUES (?, ?, ?, ?, ?)', produtos)
        
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cardapio')
def cardapio():
    return render_template('cardapio.html')

@app.route('/inicializar_db')
def inicializar_db():
    init_db()
    return jsonify({'message': 'Banco de dados inicializado com sucesso!'})

@app.route('/api/burgers')
def get_burgers():
    db = get_db()
    burgers = db.execute('SELECT * FROM burgers').fetchall()
    return jsonify([dict(burger) for burger in burgers])

@app.route('/api/combos')
def get_combos():
    db = get_db()
    combos = db.execute('SELECT * FROM combos').fetchall()
    return jsonify([dict(combo) for combo in combos])

@app.route('/api/produtos/<categoria>')
def get_produtos_por_categoria(categoria):
    db = get_db()
    produtos = db.execute('SELECT * FROM produtos WHERE categoria = ?', (categoria,)).fetchall()
    return jsonify([dict(produto) for produto in produtos])

@app.route('/fazer_pedido', methods=['POST'])
def fazer_pedido():
    pedido = request.json
    db = get_db()
    
    db.execute('''
    INSERT INTO pedidos (nome, endereco, telefone, items, total)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        pedido['nome'],
        pedido['endereco'],
        pedido['telefone'],
        json.dumps(pedido['items']),
        pedido['total']
    ))
    
    db.commit()
    return jsonify({'message': 'Pedido realizado com sucesso!'})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
