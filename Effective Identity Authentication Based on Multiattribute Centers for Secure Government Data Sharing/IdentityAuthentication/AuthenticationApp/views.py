from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
from django.core.files.storage import FileSystemStorage
import pickle
from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt
from hashlib import sha256
import io
import numpy as np
import matplotlib.pyplot as plt
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import base64
import timeit
import ipfsApi

global usersList, ownerList, requesterList, propose_time, extension_time
ipfs_api = ipfsApi.Client(host='http://127.0.0.1', port=5001)

#function to call contract
def getContract():
    global contract, web3
    blockchain_address = 'http://127.0.0.1:8545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'Authentication.json' #Authentication Contract to manage user file details
    deployed_contract_address = '0x52E73E27BDD84978a0D7257D966dFB0246c9B91D' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
getContract()

def getUsersList():
    global usersList, contract
    usersList = []
    count = contract.functions.getUserCount().call()
    for i in range(0, count):
        user = contract.functions.getUsername(i).call()
        password = contract.functions.getPassword(i).call()
        phone = contract.functions.getPhone(i).call()
        email = contract.functions.getEmail(i).call()
        address = contract.functions.getAddress(i).call()
        utype = contract.functions.getUserType(i).call()
        usersList.append([user, password, phone, email, address, utype])

def getOwnerList():
    global ownerList, contract
    ownerList = []
    count = contract.functions.getOwnerCount().call()
    for i in range(0, count):
        details = contract.functions.getDetails(i).call()
        owner = contract.functions.getOwnername(i).call()
        ownerList.append([owner, details])

def getRequesterList():
    global requesterList, contract
    requesterList = []
    count = contract.functions.getAuthenticationCount().call()
    for i in range(0, count):
        requester = contract.functions.getRequester(i).call()
        auth = contract.functions.getAuthentication(i).call()
        requesterList.append([requester, auth])
        
getUsersList()
getOwnerList()
getRequesterList()

#function to generate public and private keys for ECC algorithm
def ECCGenerateKeys():
    secret_key = generate_eth_key()
    private_key = secret_key.to_hex()  # hex string
    public_key = secret_key.public_key.to_hex()
    return private_key, public_key

#ECC will encrypt data using plain text adn public key
def ECCEncrypt(plainText, public_key):
    ecc_encrypt = encrypt(public_key, plainText)
    return ecc_encrypt

#ECC will decrypt data using private key and encrypted text
def ECCDecrypt(encrypt, private_key):
    ecc_decrypt = decrypt(private_key, encrypt)
    return ecc_decrypt

def createAttributeIdentity(username, contact, email):
    global ipfs_api, contract, requesterList, propose_time, extension_time
    start = timeit.default_timer()
    private_key, public_key = ECCGenerateKeys()#get keys for particular requester
    attributes = username+" "+contact+" "+email
    #encrypt requester using ECC keys and attributes
    requester_attribute = ECCEncrypt(attributes.encode(), public_key)
    #add requester ecc encrypted details to IPFS to get hashcode
    hashcode = ipfs_api.add_pyobj(requester_attribute)
    end = timeit.default_timer()
    propose_time = end - start #calculating ECC key generation and encryption computation time
    #extension key generation and multiattribute encryption using CHACHA20 algorithm
    start = timeit.default_timer()
    cha_key = get_random_bytes(32)
    cha_cipher = ChaCha20.new(key=cha_key)
    chacha_encrypt = cha_cipher.encrypt(attributes.encode())
    end = timeit.default_timer()
    extension_time = end - start    
    #save requester attribute hash code to IPFS api to save cost 
    msg = contract.functions.saveAuthentication(hashcode, username).transact()
    tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    requesterList.append([username, hashcode])

def Graph(request):
    if request.method == 'GET':
        global propose_time, extension_time
        height = [propose_time, extension_time + extension_time]
        bars = ['Propose ECC Algorithm', 'Extension CHACHA20 Algorithm']
        y_pos = np.arange(len(bars))
        plt.figure(figsize = (6, 3)) 
        plt.bar(y_pos, height)
        plt.xticks(y_pos, bars)
        plt.xlabel("Algorithm Names")
        plt.ylabel("Computation Time")
        plt.title("Computation Time Graph")
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        img_b64 = base64.b64encode(buf.getvalue()).decode()    
        context= {'data':"Computation Time Comaprison Graph", 'img': img_b64}
        return render(request, 'RequesterScreen.html', context)           

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def UserLogin(request):
    if request.method == 'GET':
       return render(request, 'UserLogin.html', {})

def Register(request):
    if request.method == 'GET':
        return render(request, 'Register.html', {})
    
def RegisterAction(request):
    if request.method == 'POST':
        global usersList, contract
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        utype = request.POST.get('t6', False)
        count = contract.functions.getUserCount().call()
        status = "none"
        for i in range(0, count):
            user1 = contract.functions.getUsername(i).call()
            if username == user1:
                status = "exists"
                break
        if status == "none":
            msg = contract.functions.createUser(username, password, contact, email, address, utype).transact()
            tx_receipt = web3.eth.waitForTransactionReceipt(msg)
            usersList.append([username, password, contact, email, address, utype])
            context= {'data':'New user signup details completed<br/>'+str(tx_receipt)}
            if utype == 'Requester':
                createAttributeIdentity(username, contact, email)
            return render(request, 'Register.html', context)
        else:
            context= {'data':'Given username already exists'}
            return render(request, 'Register.html', context)

def UserLoginAction(request):
    if request.method == 'POST':
        global username, contract, usersList, usertype
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "UserLogin.html"
        output = 'Invalid login details'
        for i in range(len(usersList)):
            ulist = usersList[i]
            user1 = ulist[0]
            pass1 = ulist[1]
            if user1 == username and pass1 == password:
                if ulist[5] == "Data Owner":
                    output = 'Welcome '+username
                    status = 'OwnerScreen.html'
                elif ulist[5] == "Requester":
                    output = 'Welcome '+username
                    status = 'RequesterScreen.html'
                break            
        context= {'data':output}
        return render(request, status, context)

def AdminLogin(request):
    if request.method == 'GET':
       return render(request, 'AdminLogin.html', {})

def AdminLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        status = "AdminLogin.html"
        output = 'Invalid login details'
        if username == 'admin' and password == 'admin':
            output = 'Welcome '+username
            status = 'AdminScreen.html'
        context= {'data':output}
        return render(request, status, context)

def AddOwner(request):
    if request.method == 'GET':
       return render(request, 'AddOwner.html', {})

def AddOwnerAction(request):
    if request.method == 'POST':
        global ownerList, contract
        owner = request.POST.get('t1', False)
        gender = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        aadhar = request.POST.get('t6', False)
        filename = request.FILES['t7'].name
        myfile = request.FILES['t7'].read()
        data = owner+"$"+gender+"$"+contact+"$"+email+"$"+address+"$"+aadhar+"$"+filename
        msg = contract.functions.saveOwner(data, owner).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
        ownerList.append([owner, data])
        with open("AuthenticationApp/static/files/"+filename, "wb") as file:
            file.write(myfile)
        file.close()
        context= {'data':'Owner details saved in Blockchain<br/>'+str(tx_receipt)}
        return render(request, 'AddOwner.html', context)

def DownloadFileDataRequest(request):
    if request.method == 'GET':
        name = request.GET.get('hash', False)
        with open("AuthenticationApp/static/files/"+name, "rb") as file:
            data = file.read()
        file.close()
        response = HttpResponse(data,content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename='+name
        return response        
        
def ViewOwner(request):
    if request.method == 'GET':
        global ownerList
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Data Owner</th>'
        strdata+='<th><font size="" color="black">Gender</th><th><font size="" color="black">Contact No</th>'
        strdata+='<th><font size="" color="black">Email ID</th><th><font size="" color="black">Address</th>'
        strdata+='<th><font size="" color="black">Aadhar No</th><th><font size="" color="black">Document Name</th>'
        strdata+='<th><font size="" color="black">Download Address Proof Document</th></tr>'
        for i in range(len(ownerList)):
            olist = ownerList[i]
            array = olist[1].split("$")
            strdata+='<tr><td><font size="" color="black">'+str(array[0])+'</td><td><font size="" color="black">'+array[1]+'</td><td><font size="" color="black">'+str(array[2])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[3])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[4])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[5])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[6])+'</td>'
            strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[6]+'\'><font size=3 color=black>Download File</font></a></td></tr>'                
        context= {'data':strdata}
        return render(request, 'AdminScreen.html', context)

def ViewRequester(request):
    if request.method == 'GET':
        global requesterList
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Requester Name</th>'
        strdata+='<th><font size="" color="black">Requester MultiAttribute Blockchain Verified Hashcode</th></tr>'
        for i in range(len(requesterList)):
            rlist = requesterList[i]
            strdata+='<tr><td><font size="" color="black">'+str(rlist[0])+'</td><td><font size="" color="black">'+rlist[1]+'</td></tr>'                
        context= {'data':strdata}
        return render(request, 'OwnerScreen.html', context)

def AccessData(request):
    if request.method == 'GET':
        global ownerList
        strdata = '<table border=1 align=center width=100%><tr><th><font size="" color="black">Data Owner</th>'
        strdata+='<th><font size="" color="black">Gender</th><th><font size="" color="black">Contact No</th>'
        strdata+='<th><font size="" color="black">Email ID</th><th><font size="" color="black">Address</th>'
        strdata+='<th><font size="" color="black">Aadhar No</th><th><font size="" color="black">Document Name</th>'
        strdata+='<th><font size="" color="black">Download Address Proof Document</th></tr>'
        for i in range(len(ownerList)):
            olist = ownerList[i]
            array = olist[1].split("$")
            strdata+='<tr><td><font size="" color="black">'+str(array[0])+'</td><td><font size="" color="black">'+array[1]+'</td><td><font size="" color="black">'+str(array[2])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[3])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[4])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[5])+'</td>'
            strdata+='<td><font size="" color="black">'+str(array[6])+'</td>'
            strdata+='<td><a href=\'DownloadFileDataRequest?hash='+array[6]+'\'><font size=3 color=black>Download File</font></a></td></tr>'                
        context= {'data':strdata}
        return render(request, 'RequesterScreen.html', context)    
    
