"""
! esse código não roda sozinho
(a função getJson deve ser chamada pelo servidor)
"""

import json
import re

def formata(string):
    return re.sub(r"\W", "", string)

def getJson(jsonIn:json):
    payload = json.loads(jsonIn)
    response = {}

    match payload['pedido']:

        case "cadastro":
            
            response['cadastrado'] = False
            
            if re.search(r"\w.*@\w+\.\w+", payload['email']): # só realiza o cadastro caso o email seja válido
                try: # pega os usuários já cadastrados
                    file = open("users.json", 'r')
                    aux = json.load(file)
                    file.close()

                except: # caso não haja usuários
                    aux = {}
                
                if(payload['email'] not in aux.keys()): # evita o cadastro de um email repetido
                    aux[payload['email']] = {"nome" : payload['nome'], "local" : payload['local']}
                    file = open("users.json", 'w')
                    file.write(json.dumps(aux))
                    file.close()
                    
                    file = open("chats.txt", 'a')
                    file.write(f"{payload['email']}\n")
                    file.close()

                    response['cadastrado'] = True
    
        case "login":
            
            file = open("users.json", 'r')
            aux = json.load(file)
            file.close()
            if(payload['email'] in aux.keys()):
                response['cadastrado'] = True
            else:
                response['cadastrado'] = False

        case "atualizar":
            
            file1 = open("chats.txt", 'r')
            file2 = open("users.json", 'r')
            aux = json.load(file2)
            file2.close()

            response['allUsers'] = []
            response['allGroups'] = []

            for email in file1.read().split("\n"): # lê a lista de todas as conversas
                if(email != ""):
                    if(email in aux.keys()): # separa entre grupos e usuários
                        response['allUsers'].append(email)
                    else:
                        response['allGroups'].append(email)
            response['allUsers'].sort()
            response['allGroups'].sort()
            
            file1.close()

        case "criaGrupo":
            ## payload: nome = nome do grupo, email = email do adm

            nome = formata(payload['nome'])
            response = { # cria json com as informações do grupo
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
            ## payload: nome = nome do grupo, email = user atual
            
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            response['members'].append(payload['email']) # adiciona um membro

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "sendMsg":
            ## payload: nome = nome do grupo, email = user atual, mensagem = mensagem
            
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

"""dicionario = {"pedido":"sendMsg", "email":"a@gmail.com", "mensagem":"ola grupo", "nome":"grupo legal"} # teste
print(getJson(json.dumps(dicionario)))"""
