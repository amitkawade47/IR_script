#-------------------------------------------------------------------------------
# Name:        IR_script
# Purpose:
#
# Author:      amit
#
# Created:     27/09/2018
# Copyright:   (c) amit 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os, os.path
import subprocess
import string
import json
import datetime
from subprocess import PIPE, Popen
import shutil
import pymongo
from pymongo import MongoClient


csvDbName ="Irdb_csv"
jsonDbName ="Irdb_json"

hostName = "localhost"
portNum = 27017
mongoDbName = "IrDb"
mongoCollection ="version3"

companyList = []
remoteList = []
csvFileData = []
keyCodeArray =[]
keyNameArray =[]

matchProtocol = "NEC"
csvFileHandler = ""
jsonFileHandler =""
jsonFileName =""
remoteName = ""

protocolName = ""
deviceNo = ""
subdeviceNo = ""
logFile =""
command = ""
response =""
prontoLen = 0
DEBUG = True
DEBUGFILEDATA = False #for printing file content
DEBUGCMDDATA = False #for irpMaster command respose
DEBUGPRONTO = False #for printing generated pronto
DEBUGJSON = False # for printing json
LOG = True
DBCREAT = True  #for json database log
MONGODB = True #for mongoDB connection and insertion
FILEDATA = False #for csv file data
permissionToMove = False # for moving directory from one to anather
EOF = True

def errorlog(logFileObj,log):
    logFileObj.write(log)
    print log


def main():
    ############# Creating Log file #################################
    try:
        logFileName = str(datetime.datetime.now())
        logFileName= string.replace(logFileName.split('.')[0],'-','_')
        logFileName = string.replace(logFileName,':','_')
        logFile =open(str(logFileName+"_log.txt"), "a+")
        if LOG:
            print "log file created with name: " + str(logFileName)
    except Exception as e:
        if (DEBUG | LOG):
            print "######### Log file creating error"

    ############# make MongoDB connection #########################
    if MONGODB:
        try:
            dbClient = MongoClient(hostName,portNum)
            irDb = dbClient[mongoDbName]
            irJsonCol = irDb[mongoCollection]
            if(DEBUG|LOG):
                print "Made database connection successfully"
        except Exception as e:
            if (DEBUG | LOG):
                errorlog(logFile,str(datetime.datetime.now())+ "###### Database connection ERROR[1] :" + str(e)+"\n")

    ############ Getting comapny List from database folder ########## ERROR[1]
    try:
        companyList = os.listdir(csvDbName)
        if (DEBUG):
            print "Folder open: " + str(csvDbName)
            print "Company Name: " + str(companyList)
        if(LOG):
            print "Got comapny list"
    except Exception as e:
        if (DEBUG | LOG):
            errorlog(logFile,str(datetime.datetime.now())+ "###### Folder opening error.:" + str(csvDbName)+",ERROR[1] :" + str(e)+"\n")

    ############ Creating Json database folder #################### ERROR[2]
    if DBCREAT:
        try:
            if not os.path.exists(jsonDbName):
                os.makedirs(jsonDbName)
            if (DEBUG | LOG):
                print "Folder created if not: " + str(jsonDbName)
            if(LOG):
                print "Json database folder created"
        except Exception as e:
            if (DEBUG | LOG):
                errorlog(logFile,str(datetime.datetime.now())+ "###### Folder creating error.:" + str(jsonDbName)+",ERROR[2]: "+ str(e)+"\n")

    ############ Processing one by one company #############
    try:
        for company in companyList :

            ######## Getting remote list presented in company ##### ERROR[3]
            try:
                remoteList = os.listdir(str(csvDbName+ "/"+company))
                if DEBUG:
                    print "Got remote list for company : " + str(company) + ":" + str(remoteList)
            except Exception as e:
                if (DEBUG | LOG):
                    errorlog(logFile,str(datetime.datetime.now())+ "###### Getting Remote list ERROR[3] : " + str(e)+"\n")

            ######## Processing one by on remote #############

            for remote in remoteList:
                ###### Getting remote file name ########### ERROR[4]
                try:
                    remoteName = os.listdir(str(csvDbName+ "/"+company+ "/"+remote))
                    permissionToMove = False
                except Exception as e:
                    if (DEBUG | LOG):
                        errorlog(logFile,str(datetime.datetime.now())+ "###### File not found for remote:" + str(remote) + ", for company: " + str(company)+",ERROR[4]: " +str(e)+"\n")

                ########## file opening #################### ERROR[5]
                for remoteFile in remoteName:
                    try:
                        csvFileHandler = open(str(csvDbName+ "/"+company+ "/"+remote +"/" + remoteFile),"r")
                        if (DEBUG | LOG):
                            print "File opened for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                             errorlog(logFile,str(datetime.datetime.now())+ "###### File opening error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[5]: " +str(e)+"\n")

                    ########## Reading remote csv file ############ ERROR[6]
                    try:
                        csvFileData = csvFileHandler.readlines();
                        keyCodeArray = []
                        keyNameArray = []
                        if FILEDATA:
                            print csvFileData
                        if (DEBUG | LOG):
                            print "File read successfully for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                            errorlog(logFile,str(datetime.datetime.now())+ "###### File reading error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[6]: " +str(e)+"\n")

                    ########### Parsing file data line by line AND assigning to parameters ####### ERROR[7]
                    for csvLineNo,data in enumerate(csvFileData):
                        try:
                            data =  data.split(",")
                            if(csvLineNo ==1):
                                protocolName = data[1]
                                deviceNo = data[2]
                                subdeviceNo = data[3]
                            if(csvLineNo>0):
                                keyCodeArray.append(data[4].strip())
                                keyNameArray.append(data[0])
                            if(DEBUGFILEDATA):
                                print data
                                print "Got parameters for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                        except Exception as e:
                            if (DEBUG | LOG):
                                errorlog(logFile,str(datetime.datetime.now())+"###### Parameter extracting error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[7]: " +str(e)+"\n")

                    ############### Cheking PROTOCOL in  ###################### ERROR[8]
                    try:
                        protocolCheckCommand = "irpmaster -n "+ protocolName.upper()
                        commandResp = Popen(protocolCheckCommand, shell=True, stdout=PIPE, stderr=PIPE)
                        stdout, stderr = commandResp.communicate()
                        errorMsg = "%s"% stderr
                        if errorMsg:
                            if(DEBUG|LOG):
                                print "No protocol found for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company) + ", Error:" + str(errorMsg)
                            errorlog(logFile,"No protocol found hence moving directory to another , for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)+", Error:" + str(errorMsg)+"\n")
                            permissionToMove = True
                    except Exception as e:
                        if (DEBUG | LOG):
                            errorlog(logFile,str(datetime.datetime.now())+"###### NEC protocol search error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[8]: " +str(e)+"\n")

                    ############## CSV File Closing ############################### ERROR[9]
                    try:
                        csvFileHandler.close()
                        jsonFileName =""
                        if (DEBUG | LOG):
                            print "File closed for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                             errorlog(logFile,str(datetime.datetime.now())+ "###### File closing error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[9]: " +str(e)+"\n")
                    ############ Moving company to Error Folder #################
                    if permissionToMove:
                        try:
                            errorComapnies = "Remaining_Companies"
                            if not os.path.exists(errorComapnies):
                                os.mkdir(errorComapnies)
                                if(DEBUG|LOG):
                                    print "Directory created for & with name : " + errorComapnies
                            else:
                                if(DEBUG|LOG):
                                    print "Directory already exists for & with name : " + errorComapnies

                            if not os.path.exists(errorComapnies+"/"+company):
                                os.mkdir(errorComapnies+"/"+company)
                                if(DEBUG|LOG):
                                    print "Directory created for company  & with name : " + company
                            else:
                                if(DEBUG|LOG):
                                    print "Directory already exists for company  & with name : " + company

                            if not os.path.exists(errorComapnies+"/"+company+"/"+ remote):
                                os.mkdir(errorComapnies+"/"+company+"/"+remote)
                                if(DEBUG|LOG):
                                    print "Directory created for remote  & with name : " +remote+", in company: "+ company
                            else:
                                if(DEBUG|LOG):
                                    print "Directory already exists for company  & with name : " +remote+", in company: "+ company

                            shutil.move(csvDbName+ "/"+company + "/"+remote+"/"+remoteFile ,errorComapnies+"/" +company+"/"+remote+"/" )
                            permissionToMove = False
                            errorlog(logFile,"Directory :"+  str(company) +", moved to :"+str(errorComapnies)+ ", for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)+"\n")
                            continue
                        except Exception as e:
                            errorlog(logFile,"Directory :"+  str(company) +", moving error to :"+str(errorComapnies)+ ", for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)+",ERROR[8]: " +str(e)+"\n")

                    ####### Creating company in json folder######## ERROR[10]
                    if DBCREAT:
                        try:
                            if not os.path.exists(str(jsonDbName + "/"+company)):
                                os.makedirs(str(jsonDbName + "/"+company))
                            if (DEBUG | LOG):
                                print "Folder created for company : " + str(company)
                        except Exception as e:
                            if (DEBUG | LOG):
                                errorlog(logFile,str(datetime.datetime.now())+ "###### Folder creating error for company.:" + str(company)+",ERROR[10]: "+ str(e)+"\n")

                        ###### Creating folder for remote ########## ERROR[11]
                        try:
                            if not os.path.exists(str(jsonDbName+ "/"+company+ "/"+remote)):
                                os.makedirs(str(jsonDbName+ "/"+company+ "/"+remote))
                                if (DEBUG | LOG):
                                    print "Folder created for remote : " + str(remote) + ", for company: " + str(company)
                        except Exception as e:
                            if (DEBUG | LOG):
                                errorlog(logFile,str(datetime.datetime.now())+ "###### Folder creating error for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[11]: " +str(e)+"\n")

                        ############# Creating Json File ################################ ERROR[12]
                        try:
                            jsonFileName = remoteFile.split('.')[0].replace(',','_') + ".json"
                            jsonFileHandler = open(str(jsonDbName + "/"+company+ "/"+remote +"/" + jsonFileName),"a+")
                            jsonFileHandler.write("[\n")
                            jsonLineNo =0
                            pronto =""
                            jsonData = ""
                            if (DEBUG | LOG):
                                print "Json File created for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                        except Exception as e:
                            if (DEBUG | LOG):
                               errorlog(logFile,str(datetime.datetime.now())+  "###### Json File creating error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[12]: " +str(e)+"\n")

                    ################ Creating Pronto & Json format for each key and writing to file ########################
                    for keyName, keyCode in zip(keyNameArray ,keyCodeArray):
                        ############## IrpMaster Command Execution ###################################### ERROR[13]
                        try:
                            command = "irpmaster " + "-n "+ str(protocolName) + " -p " + "D=" + str(deviceNo) + " S=" + str(subdeviceNo) + " F=" + str(keyCode)
                            response = os.popen(command).read()
                            prontoLenArray = []
                            prontoLen=0
                            if (DEBUGCMDDATA):
                                print "command for irpmaster is :" + str(command)
                                print "Command executed for key: "+ str(keyName)+", for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                                print "Command response is: " + str(response)
                        except Exception as e:
                            if (DEBUG | LOG):
                                errorlog(logFile,str(datetime.datetime.now())+ "###### Command execution error for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[13]: " +str(e)+"\n")

                        ############### Command parsing for pronto ################################## ERROR[14]
                        try:
                           pronto = string.replace(response.split('\n')[1],' ',', 0x')
                           pronto = "0x" + str(pronto)
                           prontoLen = len(pronto.split(','))
                           if (DEBUGPRONTO):
                                print "Pronto generated for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                                print "Generated pronto is: " + str(pronto)
                        except Exception as e:
                            if (DEBUG | LOG):
                                errorlog(logFile,str(datetime.datetime.now())+ "###### Pronto generation error for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[14]: " +str(e)+"\n")

                        ############## creating json format ############################## ERROR[15]
                        try:
                            jsonFormat= {"remoteName":jsonFileName.split('.')[0],"protocol": protocolName,"device": deviceNo,"subdevice": subdeviceNo,"key_code": keyCode,"key_name": keyName,"code_len": prontoLen,"pronto_code": pronto,"company":company,"deviceName": remote }
                            jsonData= json.dumps(jsonFormat)
                            if(DEBUGJSON):
                                print "Json created for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                                print "Created json is: " + str(jsonData)
                        except Exception as e:
                            if (DEBUG | LOG):
                                 errorlog(logFile,str(datetime.datetime.now())+ "###### Json creation error for key"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[15]: " +str(e)+"\n")

                        ################# Inserting in MongoDb ####################
                        if MONGODB:
                            try:
                                irJsonCol.insert_one(jsonFormat)
                                print "DB insertion done for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                            except Exception as e:
                                 if (DEBUG | LOG):
                                     errorlog(logFile,str(datetime.datetime.now())+ "###### Database insertion error for key"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[15]: " +str(e)+"\n")

                        ############# writing to file ################################## ERROR[16]
                        if DBCREAT:
                            try:
                                jsonFileHandler.write(jsonData)
                                if(jsonLineNo<len(keyCodeArray)-1):
                                   jsonFileHandler.write(",\n")
                                jsonLineNo += 1
                                if(DEBUG):
                                    print "Json written succesfully in file:"+ str(jsonFileName)+", for key :"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                            except Exception as e:
                                if (DEBUG | LOG):
                                    errorlog(logFile,str(datetime.datetime.now())+ "##### Json writting error in file:"+ str(jsonFileName)+", for key :"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+ str(company)+",ERROR[16]: " +str(e)+"\n")

                    ########### json file closed ################################## ERROR[17]
                    try:
                        jsonFileHandler.write("\n]")
                        jsonFileHandler.close()
                        if (DEBUG|LOG):
                            print "Json file closed for file :"+ str(jsonFileName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                           errorlog(logFile,str(datetime.datetime.now())+ "##### Json file closing error for file :"+ str(jsonFileName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+ str(company)+",ERROR[17]: " +str(e)+"\n")

    except Exception as e:
        if (DEBUG | LOG):
            print "error"
            print(str(datetime.datetime.now())+ "###### Folder opening error for comapany : " + str(company)+", ERROR[18]: "+ str(e)+"\n")

    if MONGODB:
        try:
            dbClient.close()
            print "DB insertion done for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
        except Exception as e:
             if (DEBUG | LOG):
                 errorlog(logFile,str(datetime.datetime.now())+ "###### Database connection clossing ERROR[15]: " +str(e)+"\n")

    try:
        logFile.close()
        if LOG:
            print "log file closed with name: " + str(logFileName)
    except Exception as e:
        if (DEBUG | LOG):
            print "######### Log file closing error"


if __name__ == '__main__':
    main()