from flask import Flask, request, jsonify

from CriaProcessos import main
import ExemploIRC as IRC

app = Flask(__name__)

def remove_email_suffix(email):
    aux = email
    aux.replace('@', '')
    return aux.replace('.', '')

@app.route('/api', methods=['GET'])
def getJson():  # put application's code here
    payload={}

    payload['pedido'] = str(request.args['pedido'])

    if('email' in request.args != None):
        payload['email'] = str(request.args['email'])

    if('mensagem' in request.args != None):
        payload['mensagem'] = str(request.args['mensagem'])

    if(payload['pedido'] == "cadastro"):
        #if("@gmail.com" in payload['email']): (a gente vai validar o email???)
        file = open("emails.txt", "a")
        file.write(f"{payload['email']}\n")
        file.close()

        aux = remove_email_suffix(payload["email"])
        file = open(f"{aux}.txt", "a")
        file.write(f"{payload['email']}\n")
        file.close()
    
    if(payload['pedido'] == "login"):
        file = open("emails.txt", 'r')
        if(payload['email'] in file.read()):
            payload['cadastrado'] = True
        else:
            payload['cadastrado'] = False
        file.close()

    if(payload['pedido'] == "atualizar"):
        file = open("emails.txt", 'r')
        payload['allUsers'] = []
        for email in file.read().split():
            payload['allUsers'].append(email)
        payload['allUsers'].sort()
        file.close()
        print(payload['allUsers'])

    print(payload)

    if(payload['pedido'] == "sendMsg"):
        print("foi")
        # print(mensagem)
        # IRC.funciona(payload['mensagem'])

    return jsonify(payload)


if __name__ == '__main__':
    app.run()