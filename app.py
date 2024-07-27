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
def getJson(jsonIn:json):
    payload = json.loads(jsonIn)
    response = {}

    match payload['pedido']:

        case "cadastro":
            if re.search(r"\w.*@\w+\.\w+", payload['email']):
                file = open("emails.txt", "a")
                file.write(f"{payload['email']}\n")
                file.close()
                
                file = open("chats.txt", "a")
                file.write(f"{payload['email']}\n")
                file.close()

                response['cadastrado'] = True

            else:
                response['cadastrado'] = False

            ## ! cadastrar nome e local do usuário
    
        case "login":
            file = open("emails.txt", 'r')
            if(payload['email'] in file.read()):
                payload['cadastrado'] = True
            else:
                payload['cadastrado'] = False
            file.close()

        case "atualizar":
            file = open("chats.txt", 'r')
            payload['allUsers'] = []
            for email in file.read().split():
                payload['allUsers'].append(email)
            payload['allUsers'].sort()
            file.close()
            # print(payload['allUsers'])
            # print(payload)

        case "criaGrupo":
            file = open("chats.txt", "a")
            file.write(f"{payload['mensagem']}\n") # mensagem = nome do grupo
            file.close()

            aux = re.sub("\W", "", payload['mensagem'])
            file = open(f"{aux}.txt", "a")
            file.write(f"{payload['email']}\n") # email = adm do grupo
            file.close()

        case "addGrupo":
            aux = re.sub("\W", "", payload['mensagem'])
            file = open(f"{aux}.txt", "a")
            file.write(f"{payload['email']}\n") # email = novo integrante do grupo
            file.close()

        case "sendMsg":
            # print(payload['mensagem'])
            # IRC.funciona(payload['mensagem'])

            ## ! definir grupo de destino

            pass

    return json.dumps(response)

    ## ! resolver o que o payload precisa voltar pro servidor


# if __name__ == '__main__':
    # app.run()

"""
dicionario = {"pedido":"criaGrupo", "email":"a@gmail.com", "mensagem":"urubu$abobrinha"} # teste
print(getJson(json.dumps(dicionario)))
"""