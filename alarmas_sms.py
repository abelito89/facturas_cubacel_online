#!/usr/bin/env
import subprocess
import json
import pprint


cmd = "df -h  | grep /dev* | awk '{ if (length($5)>2 && $5>70) print $6 " " $5 }'"
output = ""
#output1="El estado del filesystem es del 90%"
test = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
while True:
    output = test.stdout.read().decode("utf-8")
   
    if test.poll() is not None:
        break
print("%s" % (output)) 

if output != "":
  auth = "curl -k -X POST -H 'Content-Type: application/json' -d '{\"password\": \"M3d1n*2024\", \"username\": \"medin\"}\' https://172.28.97.20/auth/v1/"

  token = subprocess.Popen(auth, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
  json_token = json.loads(token.stdout.read())

  data_token = json.dumps(json_token["token"])
  token_ok = data_token.replace('"',"")
  msj=""

  for c in output:
      if c != "":
         msj += c.rstrip()
  
  lista_destinos = {"59940709","53056449","59940907","52887195","59940498","52188129"}
  for l in lista_destinos:
    ll ='"' + l +'"'
    mensaje = '"filesystems: ' + msj.rstrip() + '" '
    mensaje = mensaje.replace('%', '%, ')
    
    print (mensaje)
    
    sms = "curl -k -X POST -H \"Authorization: Bearer %s \" -H 'Content-Type: application/json' -d '{\"channel\": \"SMS\",\"sms\": {\"destination\": %s,\"message\": %s, \"sender\": \"Medin\"}}' https://172.28.97.20/notifications/v2/" % (token_ok, ll, mensaje)
    print(sms)

    enviar_sms = subprocess.Popen(sms, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)

    json_sms = json.dumps(enviar_sms.stdout.read())


 

