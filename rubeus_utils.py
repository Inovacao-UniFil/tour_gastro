
import os
import requests
import json

#Envia Lead para Rubeus
def send_lead_rubeus(name, email, phone):
    origin = os.environ.get('RUBEUS_ORIGEM')
    token = os.environ.get('RUBEUS_TOKEN')
    #Cadastrar usuario no sistema
    url = os.environ.get('RUBEUS_URL')+"/Contato/cadastro"
    data = {
        "origem": origin,
        "nome": name,
        "telefonePrincipal": phone,
        "emailPrincipal": email,
        "telefone": [
            phone
        ],
        "email": [
            email
        ],
        "token": token,
    }
    response = requests.post(url=url,data=data).json()
    print(response)
    print(response['dados'])
    #Criar evento de isncrição do curso
    url = os.environ.get('RUBEUS_URL')+"/Evento/cadastro"
    data = {
        "tipo": 578,
        "pessoa" : {
            "id": response['dados']
        },
        "descricao":"Increveu-se para Tour Gastronimia com bolsa de 40%",
        "origem": 136,
        "token": "82ce5d704d33d630cf3a05b5aa40def9"
    }
    print(data)
    response = requests.post(url=url,data=json.dumps(data),headers={"Content-Type":"application/json"}).json()
    print(response)
    return "Ok"
