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
    response = dict()

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
                    aux[payload['email']] = {
                        "nome" : payload['nome'], 
                        "local" : payload['local'],
                        "notifs" : []
                        }
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
                response = {
                    "quant" : 0,
                    "members" : [[payload['email'], aux[payload['email']]['nome']], [payload['nome'], aux[payload['nome']]['nome']]],
                    "who" : [],
                    "hist" : []
                }


                file = open(f"{nome}.json", 'w')
                json.dump(response, file)
                file.close()

                response["dados"] = aux[payload['nome']]

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

            # coloca no json do grupo
            file = open(f"{nome}.json", 'r')
            aux = json.load(file)
            file.close()

            aux['convites'].append(payload['email'])

            file = open(f"{nome}.json", 'w')
            json.dump(aux, file)
            file.close()

            #coloca no json do adm
            adm = aux['members'][0][0]

            file = open(f"users.json", 'r')
            users = json.load(file)
            file.close()

            users[adm]['notifs'].append([payload['email'], users[payload['email']]['nome'], payload['nome']])

            file = open(f"users.json", 'w')
            json.dump(users, file)
            file.close()

            response = None

        case "respostaConvite":
            ## payload: nome = nome do grupo, email = email do novo membro

            nome = formata(payload['nome'])

            file = open(f"{nome}.json", 'r')
            aux = json.load(file)
            file.close()

            file = open(f"users.json", 'r')
            users = json.load(file)
            file.close()

            aux['convites'].remove(payload['email'])

            if(payload['resposta']):
                aux['members'].append([payload['email'], users[payload['email']]['nome']])

            file = open(f"{nome}.json", 'w')
            json.dump(aux, file)
            file.close()

            adm = aux['members'][0][0]

            users[adm]['notifs'].remove([payload['email'], aux[payload['email']]['nome'], payload['nome']])

            file = open(f"users.json", 'w')
            json.dumps(users, file)
            file.close()

            response = None

        case "getPerfil":
            ## payload: email = email do usuario

            file = open(f"users.json", 'r')
            aux = json.load(file)
            file.close()

            response = aux[payload['email']]

        case "uploadFile":
            recebe_arquivo(socketIn, payload['file'])
            response = None

        case "downloadFile":
            envia_arquivo(socketIn, payload['file'])
            response = None

    if response:
        return json.dumps(response)
    else:
        return