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
            ## payload: nome = nome do grupo, email = email do adm, membros = []

            nome = formata(payload['nome'])
            response = { # cria json com as informações do grupo
                "quant" : 0,
                "members" : [payload['email']],
                "who" : [],
                "hist" : []
            }


            for membro in payload['membros']:
                response['members'].append(membro)

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

            file = open("chats.txt", 'a')
            file.write(f"{payload['nome']}\n")
            file.close()

        case "addGrupo":
            ## payload: nome = nome do grupo, membros = users a adicionar
            
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            for email in payload['membros']:
                response['members'].append(email)  # adiciona um membro

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "sendMsg":
            ## payload: nome = nome do chat (email ou grupo), email = user atual, mensagem = mensagem, grupo = true/false (é grupo ou não)

            grupo = payload['grupo']

            if(grupo):
                nome = formata(payload['nome'])
            else:
                nome1 = formata(payload['email'])
                nome2 = formata(payload['nome'])
                if(nome1 < nome2):
                    nome = nome1+nome2
                else:
                    nome = nome2+nome1

            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            response['quant'] += 1
            response['who'].append(payload['email'])
            response['hist'].append(payload['mensagem'])

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "getGrupo":
            
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

        case "getDM":
            ## payload: nome = email do destinatario, email = user atual

            nome1 = formata(payload['email']) 
            nome2 = formata(payload['nome'])
            if(nome1 < nome2):
                nome = nome1+nome2
            else:
                nome = nome2+nome1

            try: # vê se a dm já existe
                file = open(f"{nome}.json", 'r')
                response = json.load(file)
                file.close()
            except: # cria a dm
                response = {
                    "quant" : 0,
                    "members" : [payload['email'], payload['nome']],
                    "who" : [],
                    "hist" : []
                }

                file = open(f"{nome}.json", 'w')
                json.dump(response, file)
                file.close()

        case "sairGrupo":
            ## payload: nome = nome do grupo, membros = users a remover
            
            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            for email in payload['membros']:
                response['members'].remove(email) # adiciona um membro

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

    return json.dumps(response)

# dicionario = {"pedido":"cadastro", "email":"j@gmail.com", "nome":"J", "local": "Brasil"} # teste
# print(getJson(json.dumps(dicionario)))
# {"cadastrado": true}

# dicionario = {"pedido":"login", "email":"j@gmail.com"}
# print(getJson(json.dumps(dicionario)))
# {"cadastrado": true}

# dicionario = {"pedido":"atualizar"}
# print(getJson(json.dumps(dicionario)))
# {"allUsers": ["j@gmail.com"], "allGroups": []}

# dicionario = {"pedido":"cadastro", "email":"o@gmail.com", "nome":"O", "local": "EUA"}
# print(getJson(json.dumps(dicionario)))
# {"cadastrado": true}

# dicionario = {"pedido":"atualizar"}
# print(getJson(json.dumps(dicionario)))
# {"allUsers": ["j@gmail.com", "o@gmail.com"], "allGroups": []}

# dicionario = {"pedido": "getDM", "email": "j@gmail.com", "destinatario": "o@gmail.com"}
# print(getJson(json.dumps(dicionario)))
# {"quant": 0, "members": ["j@gmail.com", "o@gmail.com"], "who": [], "hist": []}

# dicionario = {"pedido": "sendDM", "destinatario": "o@gmail.com", "email": "j@gmail.com", "mensagem": "oi"} // antigo
# print(getJson(json.dumps(dicionario)))
# {"quant": 1, "members": ["j@gmail.com", "o@gmail.com"], "who": ["j@gmail.com"], "hist": ["oi"]}

# dicionario = {"pedido": "sendMsg", "nome": "j@gmail.com", "email": "o@gmail.com", "mensagem": "eae", "grupo": False} // novo
# print(getJson(json.dumps(dicionario)))
# {"quant": 2, "members": ["j@gmail.com", "o@gmail.com"], "who": ["j@gmail.com", "o@gmail.com"], "hist": ["oi", "eae"]}