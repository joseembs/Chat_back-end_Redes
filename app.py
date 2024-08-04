"""
! esse código não roda sozinho
(a função getJson deve ser chamada pelo servidor)
"""

import json
import re

from server import recebe_arquivo, envia_arquivo


def formata(string):
    return re.sub(r"\W", "", string)

def getJson(jsonIn:json, socketIn):
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
                    response['dados'] = {"email" : payload['email'], "nome" : payload['nome'], "local" : payload['local']}

        case "login":

            file = open("users.json", 'r')
            aux = json.load(file)
            file.close()
            if(payload['email'] in aux.keys()):
                response['cadastrado'] = True
                response['dados'] = {"email" : payload['email'], "nome" : aux[payload['email']]['nome'], "local" : aux[payload['email']]['local']}
            else:
                response['cadastrado'] = False

        case "atualizar":

            file1 = open("chats.txt", 'r')
            file2 = open("users.json", 'r')
            aux = json.load(file2)
            file2.close()

            response['allUsers'] = {}
            response['allGroups'] = []

            for email in file1.read().split("\n"): # lê a lista de todas as conversas
                if(email != ""):
                    if(email in aux.keys()): # separa entre grupos e usuários
                        response['allUsers'].update({email: aux[email]['nome']})
                    else:
                        response['allGroups'].append(email)
            response['allUsers'] = dict(sorted(response['allUsers'].items(),key=lambda item: item[1]))
            response['allGroups'].sort()

            file1.close()

        case "criaGrupo":
            ## payload: nome = nome do grupo, email = email do adm, membros = [emails]
            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            nome = formata(payload['nome'])
            response = { # cria json com as informações do grupo
                "quant" : 0,
                "members" : [[payload['email'], aux[payload['email']]['nome']]],
                "who" : [],
                "hist" : [],
                "convites" : []
            }


            for membro in payload['membros']:
                response['members'].append([membro, aux[membro]['nome']]) # o payload vai mandar o email ou o nome dos membros?

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

            file = open("chats.txt", 'a')
            file.write(f"{payload['nome']}\n")
            file.close()

        case "addGrupo":
            ## payload: nome = nome do grupo, membros = users a adicionar
            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            for membro in payload['membros']:
                response['members'].append([membro, aux[membro]['nome']])  # adiciona um membro

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

            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            response['quant'] += 1
            response['who'].append([payload['email'], aux[payload['email']]['nome']])
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
            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            nome1 = formata(payload['email'])
            nome2 = formata(payload['nome'])
            if(nome1 < nome2):
                nome = nome1+nome2
            else:
                nome = nome2+nome1

            try: # vê se a dm já existe
                file = open(f"{nome}.json", 'r')
                response = json.load(file)
                response["dados"] = aux[payload['nome']]
                file.close()
            except: # cria a dm
                print("?")
                response = {
                    "quant" : 0,
                    "members" : [[payload['email'], aux[payload['email']]['nome']], [payload['nome'], aux[payload['nome']]['nome']]],
                    "who" : [],
                    "hist" : []
                }
                print("??")


                file = open(f"{nome}.json", 'w')
                json.dump(response, file)
                file.close()

                response["dados"] = aux[payload['nome']]
                print("???")

        case "sairGrupo":
            ## payload: nome = nome do grupo, membros = users a remover

            nome = formata(payload['nome'])
            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            for membro in payload['membros']:
                for info in response['members']: # info = [email, nome]
                    if membro in info:
                        response['members'].remove(info) # remove um membro

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "enviaConvite":
            ## payload: nome = nome do grupo, email = email do novo membro

            nome = formata(payload['nome'])

            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            response['convites'].append(payload['email'])

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "respostaConvite":
            ## payload: nome = nome do grupo, email = email do novo membro

            nome = formata(payload['nome'])

            file = open(f"{nome}.json", 'r')
            response = json.load(file)
            file.close()

            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            response['convites'].remove(payload['email'])
            response['members'].append([payload['email'], aux[payload['email']]['nome']])

            file = open(f"{nome}.json", 'w')
            json.dump(response, file)
            file.close()

        case "getPerfil":
            ## payload: email = email do usuario

            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            response = aux[payload['email']]

        case "uploadFile":
            recebe_arquivo(socketIn, payload['file'])

            # response = {"result": "foi"}

        case "downloadFile":
            envia_arquivo(socketIn, payload['file'])

            # response = {"result": "foi"}


    return json.dumps(response)

# dicionario = {"pedido":"cadastro", "email":"j@gmail.com", "nome":"J", "local": "Brasil"} # teste
# print(getJson(json.dumps(dicionario)))
# {"cadastrado": true}

# dicionario = {"pedido":"getPerfil", "email":"j@gmail.com"}
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