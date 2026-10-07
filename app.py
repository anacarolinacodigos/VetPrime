import base64
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chave_segredo_vetprime'
app.permanent_session_lifetime = timedelta(minutes=10)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # <-- COLOQUE A SUA SENHA DO MYSQL HERE
        database='vetprime'
    )

def codificar_cpf(cpf):
    return base64.b64encode(cpf.encode('utf-8')).decode('utf-8')

def decodificar_cpf(cpf_codificado):
    try:
        return base64.b64decode(cpf_codificado.encode('utf-8')).decode('utf-8')
    except Exception:
        return cpf_codificado

def usuario_logado():
    return 'usuario' in session

@app.route('/')
def index():
    erro = request.args.get('erro')
    return render_template('login.html', erro=erro)

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE email = %s AND senha = %s', (email, senha))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario:
        session.permanent = True
        session['usuario'] = usuario
        return redirect('/tutores')
    else:
        return redirect('/?erro=E-mail ou senha incorretos')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/api/usuario-logado')
def api_usuario_logado():
    if not usuario_logado():
        return jsonify({'erro': 'Não autorizado'}), 401
    return jsonify({'nome': session['usuario']['nome']})

@app.route('/tutores')
def tela_tutores():
    if not usuario_logado():
        return redirect('/?erro=Sessao expirada ou acesso nao autorizado')
    return render_template('tutores.html')

@app.route('/api/tutores', methods=['GET'])
def listar_tutores():
    if not usuario_logado():
        return jsonify([]), 401
    
    busca = request.args.get('busca', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tutores WHERE nome LIKE %s', (f'%{busca}%',))
    tutores = cursor.fetchall()
    cursor.close()
    conn.close()

    for t in tutores:
        t['cpf'] = decodificar_cpf(t['cpf_criptografado'])

    return jsonify(tutores)

@app.route('/api/tutores', methods=['POST'])
def cadastrar_tutor():
    if not usuario_logado():
        return redirect('/')
    
    nome = request.form.get('nome')
    cpf = request.form.get('cpf')
    telefone = request.form.get('telefone')
    cpf_cripto = codificar_cpf(cpf)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tutores (nome, cpf_criptografado, telefone) VALUES (%s, %s, %s)',
        (nome, cpf_cripto, telefone)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/tutores')

@app.route('/pets')
def tela_pets():
    if not usuario_logado():
        return redirect('/?erro=Sessao expirada ou acesso nao autorizado')
    return render_template('pets.html')

@app.route('/api/pets', methods=['GET'])
def listar_pets():
    if not usuario_logado():
        return jsonify([]), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT pets.*, tutores.nome AS nome_tutor 
        FROM pets 
        LEFT JOIN tutores ON pets.tutor_id = tutores.id
    ''')
    pets = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(pets)

@app.route('/api/pets', methods=['POST'])
def cadastrar_pet():
    if not usuario_logado():
        return redirect('/')
    
    nome = request.form.get('nome')
    especie = request.form.get('especie')
    raca = request.form.get('raca')
    tutor_id = request.form.get('tutor_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO pets (nome, especie, raca, tutor_id) VALUES (%s, %s, %s, %s)',
        (nome, especie, raca, tutor_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/pets')

@app.route('/agendamentos')
def tela_agendamentos():
    if not usuario_logado():
        return redirect('/?erro=Sessao expirada ou acesso nao autorizado')
    return render_template('agendamentos.html')

@app.route('/api/agendamentos', methods=['GET'])
def listar_agendamentos():
    if not usuario_logado():
        return jsonify([]), 401
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT 
          agendamentos.*, 
          tutores.nome AS nome_tutor, 
          tutores.cpf_criptografado, 
          pets.nome AS nome_pet, 
          pets.especie AS especie_pet 
        FROM agendamentos
        JOIN tutores ON agendamentos.tutor_id = tutores.id
        JOIN pets ON agendamentos.pet_id = pets.id
        ORDER BY agendamentos.mes ASC, agendamentos.data_agendamento ASC
    ''')
    agendamentos = cursor.fetchall()
    cursor.close()
    conn.close()

    for a in agendamentos:
        a['cpf_tutor'] = decodificar_cpf(a['cpf_criptografado'])

    return jsonify(agendamentos)

@app.route('/api/agendamentos', methods=['POST'])
def cadastrar_agendamento():
    if not usuario_logado():
        return redirect('/')
    
    data_agendamento = request.form.get('data_agendamento')
    mes = request.form.get('mes')
    observacao = request.form.get('observacao')
    tutor_id = request.form.get('tutor_id')
    pet_id = request.form.get('pet_id')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO agendamentos (data_agendamento, mes, observacao, tutor_id, pet_id) VALUES (%s, %s, %s, %s, %s)',
        (data_agendamento, mes, observacao, tutor_id, pet_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/agendamentos')

if __name__ == '__main__':
    app.run(debug=True, port=5000)