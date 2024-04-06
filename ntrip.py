import urllib3 
import os
import telebot
import socket
import base64
import sys
import time

BOT_TOKEN = '11223344556677889900AABBCCDDEE' #bot token goes here

bot = telebot.TeleBot(BOT_TOKEN)

botChatID = 112233445566 #the id of the chat goes here

noConnection = 0        #no connection to caster
noData = 0              #no data received
mountpointError = 0     #Invalid or no mountpoint
unknownError = 0        #unknown error
unknownError2 = 0       #unknown error#2
prev = time.time() -5   #timer
curr = 0                #variables
debugMode = False       #set to true to print statements sent to bot

# base station data
server = "serverIPOrDomain"
port = "2101" #default
mountpoint = "YourMTPT"
username = "yourUserName"
password = "yourPasswd"


#time to let computer start
time.sleep(60)
print("starting")
def printMode(string1):
    if debugMode:
        print (string1)
    bot.send_message(botChatID, string1)

    
def getHTTPBasicAuthString(username,password):
    inputstring = username + ':' + password
    pwd_bytes = base64.encodebytes(inputstring.encode("utf-8"))
    pwd = pwd_bytes.decode("utf-8").replace('\n','')
    return pwd
    
pwd = getHTTPBasicAuthString(username,password)
    
header =\
"GET /{} HTTP/1.0\r\n".format(mountpoint) +\
"User-Agent: NTRIP u-blox\r\n" +\
"Accept: */*\r\n" +\
"Authorization: Basic {}\r\n".format(pwd) +\
"Connection: close\r\n\r\n"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(20)

while True: #run forever
    time.sleep(.1)
    try: 
        print("in while")
        if curr - prev >= 5: #run every 5 sec. Can change to your own interval.
            print("in timer")
                             #Sooner will use more data, but warn you sooner.
            prev = time.time()
            bs = "bs1"
        
            #this all just checks all the variables and sends if necessary
                #The idea here is that any fail must happen twice in a row to avoid the random missed sentence or anything.
            if noConnection == 2:
                printMode("Bot Warning Message:\nNo connection to caster")
            elif noData == 2:
                printMode("Bot Warning Message:\nNo Data\nConnected to caster, but no data-receiver unplugged?")
            elif mountpointError == 2:
                printMode("Bot Warning Message:\nInvalid credentials or no mountpoint")
            elif unknownError == 2:
                printMode("Bot Warning Message:\nError-Either base down or script is not working")
            elif unknownError2 == 2:
                printMode("Bot Warning Message:\nError-Either base down or script is not working")
                print("past checks")
        
        
        try:
            s.connect((server,int(port)))
            s.sendto(header.encode('utf-8'),(server,int(port)))
            resp = s.recv(1024)
        except:
            #no connection to caster
            noConnection += 1
        else:
            noConnection = 0
            if resp.startswith(b"STREAMTABLE"):
                #invalid or no mountpoint
                mountpointError += 1 
                continue 
            elif not resp.startswith(b"HTTP/1.1 200 OK"):
                printMode("Bot Startup Message:\nScript running")
                mountpointError = 0
                unknownError = 0
            else:
                unknownError += 1
            try:
                while True: #run till broken out by child statements
                    data = s.recv(1024)
                    unknownError2 = 0
      
                    if not data:
                        noData += 1
                        break
                    else:
                        noData = 0
            except:
                unknownError = unknownError2 + 1
            finally:
                s.close()
                print("keyboard int")
                sys.exit(0)
    except KeyboardInterrupt:
        print("interrupted")
