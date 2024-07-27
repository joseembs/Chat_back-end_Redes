"""
! esse código não roda sozinho, ele é só um monte de funções
(elas devem ser chamadas pelo servidor em algum momento)

LEGENDA
comentário no final da linha de código: explica a linha em que ele está
comentário sozinho na linha:
    # = linhas antigas que eu comentei
    ## = coisas pra fazer depois
        ! = precisa
        ? = não precisa

no começo do código tem alguns imports velhos de quando a gente tava usando flask (rip)
no final do código tem um teste que eu to usando pra rodar o código sozinho
"""

import json
import re

#from flask import Flask, request, jsonify
#from CriaProcessos import main
#import ExemploIRC as IRC

# app = Flask(__name__)

# @app.route('/api', methods=['GET'])

def formata(string):
    return re.sub(r"\W", "", string)


def getJson(jsonIn:json):
    payload = json.loads(jsonIn)
    response = {}

    match payload['pedido']:

        case "cadastro":
            if re.search(r"\w.*@\w+\.\w+", payload['email']):
                try:
                    file = open("users.json", 'r')
                    aux = json.load(file)
                    file.close()

                except:
                    aux = {}
                
                if(payload['email'] not in aux.keys()):
                    aux[payload['email']] = {"nome" : payload['nome'], "local" : payload['local']}
                    file = open("users.json", 'w')
                    file.write(json.dumps(aux))
                    file.close()
                    
                    file = open("chats.txt", 'a')
                    file.write(f"{payload['email']}\n")
                    file.close()

                    response['cadastrado'] = True
                else:
                    response['cadastrado'] = False

            else:
                response['cadastrado'] = False
    
        case "login":
            file = open("users.json", 'r')
            if(payload['email'] in file.read()):
                response['cadastrado'] = True
            else:
                response['cadastrado'] = False
            file.close()

        case "atualizar":
            file1 = open("chats.txt", 'r')
            file2 = open("users.json", 'r')
            aux = json.load(file2)
            file2.close()

            response['allUsers'] = []
            response['allGroups'] = []

            for email in file1.read().split("\n"):
                if(email != ""):
                    if(email in aux.keys()):
                        response['allUsers'].append(email)
                    else:
                        response['allGroups'].append(email)
            response['allUsers'].sort()
            response['allGroups'].sort()
            file1.close()

        case "criaGrupo":
            # payload: nome = nome do grupo, email = email do adm

            """# caso dm?
            if('nome' in payload.keys()):
                nome = formata(payload['nome'])
            else: 
                nome1 = formata(payload['email']) 
                nome2 = formata(payload['destinatario'])
                if(nome1 < nome2):
                    nome = nome1+nome2
                else:
                    nome = nome2+nome1"""

            nome = formata(payload['nome'])
            response = {
                "quant" : 0,
                "members" : [payload['email']],
                "who" : [],
                "hist" : []
            }

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

            file = open("chats.txt", 'a')
            file.write(f"{payload['nome']}\n")
            file.close()

        case "addGrupo":
            # payload: nome = nome do grupo, email = user atual
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            response['members'].append(payload['email'])

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "sendMsg":
            # payload: nome = nome do grupo, email = user atual, mensagem = mensagem
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            response['quant'] += 1
            response['who'].append(payload['email'])
            response['hist'].append(payload['mensagem'])

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()
        
        case "getHistorico":
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

    return json.dumps(response)

dicionario = {"pedido":"sendMsg", "email":"a@gmail.com", "mensagem":"ola grupo", "nome":"grupo legal"} # teste
print(getJson(json.dumps(dicionario)))