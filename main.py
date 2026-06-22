from flask import Flask, render_template, request, redirect
from pathlib import Path
import os
import psycopg2
from dotenv import load_dotenv
import requests
import json
from unidecode import unidecode
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta, timezone, time, date
from flask import render_template
from rubeus_utils import send_lead_rubeus
from gmail_utils import send_email, define_student_email, define_teacher_email, create_calendar

load_dotenv()
app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

time_table = {
    'segunda': ["08:00" , "12:00"],
    'terça'  : ["13:30" , "17:30"],
    'quarta' : ["08:00" , "12:30"],
    'quinta' : ["13:30" , "17:30"],
    'sexta'  : ["08:30" , "12:30"],
    'sabado' : ["00:30" , "00:00"],
    'domingo': ["00:30" , "00:00"]
}

#Cria lista de horarios para seleção
def generate_intervals(start, end, delta):
    current = start
    time_list = []
    while current <= end:
        time_list.append(current.strftime("%H:%M"))
        current = (datetime.combine(date.today(), current) + delta).time()
    return time_list

MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_ PASSWORD')

#Remove horarios já alocados
def get_valid_times(s_date):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM gastro WHERE agendamento_date = %s;", [s_date.isoformat()])
    all = cur.fetchall()
    weekday = s_date.weekday()
    weekday_time = time_table[list(time_table.keys())[weekday]]
    start_time = time.fromisoformat(weekday_time[0])
    end_time = time.fromisoformat(weekday_time[1])
    scheduling = generate_intervals(start_time,end_time,timedelta(minutes=30))
    for get in all:
        entry_time = get[4]
        print(entry_time)
        entry_time = datetime.fromisoformat(str(entry_time)).strftime("%H:%M")
        if entry_time in scheduling:
            scheduling.remove(entry_time)
    return scheduling

#Encriptar dados usando uma chave do ambiente
def encrypt(value):
    encrypted_value = ""
    key_index = 0
    value = value
    key = os.environ.get('ENCRYPT_KEY')
    for value_index in range(len(value)):
        char_value = (ord(value[value_index]) + ord(key[key_index]))
        if char_value > 126:
            char_value -= (127-32)
        if char_value < 32:
            char_value += 32
        char = chr(char_value) 
        encrypted_value+=char
        key_index+=1
        if key_index >= len(key): key_index=0
    return encrypted_value

#Desencriptar dados usando uma chave do ambiente
def decrypt(value):
    encrypted_value = ""
    key_index = 0
    value = value
    key = os.environ.get('ENCRYPT_KEY')
    for value_index in range(len(value)):
        char_value = (ord(value[value_index]) - ord(key[key_index]))
        if char_value < 32:
            char_value += (127-32)
        if char_value < 32:
            char_value += (32)
        char = chr(char_value) 
        encrypted_value+=char
        key_index+=1
        if key_index >= len(key): key_index=0
    return encrypted_value

app.config['static_folder'] = BASE_DIR / 'static'

#Conectar banco
def get_db_connection():
    conn = psycopg2.connect(hostaddr=os.environ.get('DB_HOST'),
                            port=os.environ.get('DB_PORT'),
                            user=os.environ.get('UNFL_USERNAME'),
                            password=os.environ.get('UNFL_PASSWORD'),
                            database=os.environ.get('UNFL_NAME'))
    return conn

@app.route("/")
def main():
    #Conectar Banco
    conn = get_db_connection()
    cur = conn.cursor()
    #Criar tabela se não existe
    cur.execute("CREATE TABLE IF NOT EXISTS unifilista.gastro (id serial PRIMARY KEY, nome text, email text, telefone text, agendamento_time timestamp, agendamento_date timestamp, codigo smallserial, horario timestamp);")
    conn.commit()
    #Encerrar conexao
    cur.close()
    conn.close()
    start_date = datetime(year=2026,month=6,day=23)
    end_date = datetime(year=2026,month=7,day=17)
    scheduling = {}
    for day in time_table.keys():
        start_time = time.fromisoformat(time_table[day][0])
        end_time = time.fromisoformat(time_table[day][1])
        scheduling[day] = generate_intervals(start_time,end_time,timedelta(minutes=30))
    data = {
        "start_date" : start_date.strftime("%Y-%m-%d"),
        "end_date" : end_date.strftime("%Y-%m-%d"),
        "scheduling": scheduling
    }
    print(data)
    return render_template('index.html', data=data)

@app.route("/consultar")
def consultar():
    return render_template('consultar.html')

#Adiciona o usuario ao banco de dados
@app.route("/send_data", methods=["POST"])
def send_data():
    data = request.json
    email = (data.get("email").lower())
    nome = encrypt(data.get("nome"))
    telefone = encrypt(data.get("telefone"))
    agendamento_date = data.get("date")
    agendamento_time = data.get("time")
    print(agendamento_date)
    print(agendamento_time)
    agendamento_date = datetime.fromisoformat(agendamento_date)
    agendamento_time = datetime.combine(agendamento_date, time.fromisoformat(agendamento_time))
    print(agendamento_date)
    print(agendamento_time)
    #Conectar Banco
    print("Conectar")
    conn = get_db_connection()
    print("Conectado")
    cur = conn.cursor()
    #Criar tabela se não existe
    cur.execute("CREATE TABLE IF NOT EXISTS unifilista.gastro (id serial PRIMARY KEY, nome text, email text, telefone text, agendamento_time timestamp, agendamento_date timestamp, codigo smallserial, horario timestamp);")    #Verificar se aluno é duplicado
    cur.execute(f"SELECT * FROM gastro WHERE email = %s;", [email])
    get = cur.fetchone()
    if get:
        #Aluno duplicado
        codigo = get[6]
        cur.close()
        conn.close()
        agendamento_time = get[4]
        agendamento_date = get[5]
        redirection_url = Flask.url_for(app,endpoint='success')+f"?comprovante=CONF{str(codigo).zfill(6)}&new=False&date={agendamento_date.strftime("%d/%m/%Y")}&time={agendamento_time.strftime("%H:%M")}"
        print(redirection_url)
        return {
            "success": f"Aluno já cadastrou.",
            "codigo": f"CONF{str(codigo).zfill(6)}",
            "date": agendamento_date,
            "time": agendamento_time,
            "new": False,
            "url": redirection_url
            }
    else:
        
        #redirection_url = Flask.url_for(app,endpoint='success')+f"?comprovante=Encerrada&new=True"
        #return {
        #    "success": f"Not Permited.",
        #    "codigo": f"NONE",
        #    "new": True,
        #    "url": redirection_url
        #    }
        #Inserir dados Aluno
        cur.execute(f"INSERT INTO gastro (nome, email, telefone, agendamento_time, agendamento_date, horario) VALUES" + 
                    f"(%s,%s,%s,%s,%s, CURRENT_TIMESTAMP);",[nome,email,telefone,agendamento_time.isoformat(),agendamento_date.isoformat()])
        conn.commit()
        #Receber Codigo de confirmacao conexao
        cur.execute(f"SELECT * FROM gastro WHERE email = %s;", [email])
        get = cur.fetchone()
        codigo = get[6]
        agendamento_date = get[5]
        agendamento_time = get[4]
        cur.close()
        conn.close()
        #Enviar para CRM
        crm_nome = data.get("nome").upper()
        crm_email = data.get("email").upper()
        crm_telefone = data.get("telefone")
        send_lead_rubeus(crm_nome,crm_email,crm_telefone)
        #Redirecionar
        redirection_url = Flask.url_for(app,endpoint='success')+f"?comprovante=CONF{str(codigo).zfill(6)}&new=True&date={agendamento_date.strftime("%d/%m/%Y")}&time={agendamento_time.strftime("%H:%M")}"
        print(redirection_url)
        message = define_student_email(agendamento_date.strftime("%d/%m/%Y"),agendamento_time.strftime("%H:%M"),f"CONF{str(codigo).zfill(6)}")
        send_email("Tour Gastronomia: Agendamento",message,None,crm_email)
        message = define_teacher_email(agendamento_date.strftime("%d/%m/%Y"),agendamento_time.strftime("%H:%M"),crm_nome,crm_email)
        send_email("Tour Gastronomia: Novo Agendamento",message,None,"gastronomia@unifil.br")
        create_calendar(agendamento_date.strftime("%Y-%m-%d")+" "+agendamento_time.strftime("%H:%M:%S"),crm_email)
        return {
            "success": f"Sucesso.",
            "codigo": f"CONF{str(codigo).zfill(6)}",
            "date": agendamento_date,
            "time": agendamento_time,
            "new": True,
            "url": redirection_url
            }

#Popula o Excel de usuarios que se inscreveram
#@app.route("/getdata")
def getdata():
    comp = request.args.get("comprovante") 
    print(comp)
    #Conectar Banco
    print("Conectar")
    conn = get_db_connection()
    print("Conectado")
    cur = conn.cursor()
    #Verificar se aluno é duplicado
    #cur.execute(f"SELECT * FROM gastro WHERE codigo = %s;", [comp])
    cur.execute(f"SELECT * FROM gastro")
    student_list = []
    all = cur.fetchall()
    for get in all:
        id = get[0]
        name = decrypt(get[1])
        email = (get[2])
        telefone = decrypt(get[3])
        time = get[4].strftime("%H:%M")
        date = get[5].strftime("%d/%m/%y")
        code = get[6]
        s_date = get[7].strftime("%d/%m/%y")
        data = [name,email,telefone,date,time,code,s_date]
        student_list.append(data)
    df = pd.DataFrame(data=student_list,columns=["Nome","Email","Telefone","Data","Horario","Código de Confirmação","Data de cadastro"])
    Path(BASE_DIR / "gastro.xlsx").touch()
    print(BASE_DIR / "gastro.xlsx")
    df.to_excel(excel_writer = BASE_DIR / "gastro.xlsx")
    cur.close()
    conn.close()
    return render_template('sucesso.html')

@app.route('/consult', methods=["POST"])
def consult():
    #Conectar Banco
    print("Conectar")
    conn = get_db_connection()
    print("Conectado")
    cur = conn.cursor()
    data = request.json
    if(data.get("comprovante")):
        comprovante = data.get("comprovante")
        codigo = int(comprovante[4:])
        cur.execute(f"SELECT * FROM gastro WHERE codigo = %s;", [codigo])
    else:
        email = (data.get("email").lower())
        telefone = encrypt(data.get("telefone"))  
        cur.execute(f"SELECT * FROM gastro WHERE email = %s AND telefone = %s;", [email, telefone])
    get = cur.fetchone()
    if get:
        #Aluno duplicado
        codigo = get[6]
        cur.close()
        conn.close()
        agendamento_time = get[4]
        agendamento_date = get[5]
        redirection_url = Flask.url_for(app,endpoint='success')+f"?comprovante=CONF{str(codigo).zfill(6)}&new=False&date={agendamento_date.strftime("%d/%m/%Y")}&time={agendamento_time.strftime("%H:%M")}"
        print(redirection_url)
        return {
            "success": f"Aluno já cadastrou.",
            "codigo": f"CONF{str(codigo).zfill(6)}",
            "date": agendamento_date,
            "time": agendamento_time,
            "new": False,
            "url": redirection_url
            }
    else:
        redirection_url = Flask.url_for(app,endpoint='failed')
        return {
            "success": f"Aluno não encontrado.",
            "url": redirection_url
            }
    get = cur.fetchone()


#@app.route('/test_email')
def test_email():
    message = define_teacher_email("22/02/2022","22:22","Teste","Teste@teste.teste")
    send_email("Tour Gastronomia: Agendamento",message,None,"rotaloco30@gmail.com")
    return "ok"

#@app.route('/test_calendar')
def test_calendar():
    date_time = datetime(2025,9,25,16,30).isoformat()
    create_calendar(date_time,'rgalletto@unifil.br')
    return "ok"
        
#@app.route('/test_rubeus')
def test_rubeus():
    return send_lead_rubeus("John Dude","test@test.com","43999999999")

#Responde com uma lista de dias validos com base na data recebida
@app.route('/get_valid_times', methods=['POST'])
def valid_times():
    data = request.json
    print(data.get('date'))
    s_date = data.get('date')
    s_date = datetime.fromisoformat(s_date)
    print(s_date)
    return get_valid_times(s_date)

#Rota de sucesso
@app.route("/success")
def success():
    return render_template('sucesso.html')

@app.route('/failed')
def failed():
    return render_template('failed.html')

