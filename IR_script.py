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


csvDbName ="Irdb_csv"
jsonDbName ="Irdb_json"

companyList = []
remoteList = []
csvFileData = []
keyCodeArray =[]
keyNameArray =[]


csvFileHandler = ""
jsonFileHandler =""
jsonFileName =""
remoteName = ""

protocolName = ""
deviceNo = ""
subdeviceNo = ""

command = ""
response =""
prontoLen = 0

DEBUG = True
DEBUGFILEDATA = False #for printing file content
DEBUGCMDDATA = False #for irpMaster command respose
DEBUGPRONTO = False #for printing generated pronto
DEBUGJSON = True # for printing json
LOG = True
DBCREAT = False  #for json database log
FILEDATA = False #for csv file data

EOF = True
def main():
    ############ Getting comapny List from database folder ##########
    try:
        companyList = os.listdir(csvDbName)
        if (DEBUG):
            print "Folder open: " + str(csvDbName)
            print "Company Name: " + str(companyList)
        if(LOG):
            print "Got comapny list"
    except Exception as e:
        if (DEBUG | LOG):
            print   "###### Folder opening error.:" + str(csvDbName)+",ERROR[1] :" + str(e)

    ############ Creating Json database folder ####################
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
                print   "###### Folder creating error.:" + str(jsonDbName)+",ERROR[2]: "+ str(e)

    ############ Processing one by one company #############
    try:
        for company in companyList :
            ####### Creating company in json database ########
            if DBCREAT:
                try:
                    if not os.path.exists(str(jsonDbName + "/"+company)):
                        os.makedirs(str(jsonDbName + "/"+company))
                    if (DEBUG | LOG):
                        print "Folder created for company : " + str(company)
                except Exception as e:
                    if (DEBUG | LOG):
                        print   "###### Folder creating error for company.:" + str(company)+",ERROR[3]: "+ str(e)

            ######## Getting remote list presented in company #####
            try:
                remoteList = os.listdir(str(csvDbName+ "/"+company))
                if DEBUG:
                    print "Got remote list for company : " + str(company) + ":" + str(remoteList)
            except Exception as e:
                if (DEBUG | LOG):
                    print "###### Getting Remote list ERROR[4] : " + str(e)

            ######## Processing one by on remote #############

            for remote in remoteList:

                ###### Creating folder for remote ##########
                if DBCREAT:
                    try:
                        if not os.path.exists(str(csvDbName+ "/"+company+ "/"+remote)):
                            os.makedirs(str(csvDbName+ "/"+company+ "/"+remote))
                        if (DEBUG | LOG):
                            print "Folder created for remote : " + str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                            print "###### Folder creating error for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[5]: " +str(e)

                ###### Getting remote file name ###########
                try:
                    remoteName = os.listdir(str(csvDbName+ "/"+company+ "/"+remote))
                except Exception as e:
                    if (DEBUG | LOG):
                        print "###### File not found for remote:" + str(remote) + ", for company: " + str(company)+",ERROR[6]: " +str(e)

                ########## file opening ####################
                for remoteFile in remoteName:
                    try:
                        csvFileHandler = open(str(csvDbName+ "/"+company+ "/"+remote +"/" + remoteFile),"r")
                        if (DEBUG | LOG):
                            print "File opened for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                             print "###### File opening error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[7]: " +str(e)

                    ########## Reading remote csv file ############
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
                             print "###### File reading error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[8]: " +str(e)

                    ########### Parsing file data line by line AND assigning to parameters #######
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
                                print "###### Parameter extracting error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[9]: " +str(e)

                    ############## CSV File Closing ###############################
                    try:
                        csvFileHandler.close()
                        if (DEBUG | LOG):
                            print "File closed for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                             print "###### File closing error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[10]: " +str(e)

                    ############# Creating Json File ################################
                    #if DBCREAT:
                    try:
                        jsonFileName = remoteFile.split('.')[0].replace(',','_') + ".json"
                       # jsonFileHandler = open(str(jsonDbName + "/"+company+ "/"+remote +"/" + jsonFileName),"a")
                        jsonLineNo =0
                        if (DEBUG | LOG):
                            print "Json File created for remote file: " +str(remoteFile)+", for remote: "+ str(remote) + ", for company: " + str(company)
                    except Exception as e:
                        if (DEBUG | LOG):
                             print "###### Json File creating error for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[11]: " +str(e)

                    ################ Creating Pronto & Json format for each key and writing to file ########################
                    for keyName, keyCode in zip(keyNameArray ,keyCodeArray):
                        ############## IrpMaster Command Execution ######################################
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
                                 print "###### Command execution error for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[12]: " +str(e)

                        ############### Command parsing for pronto ##################################
                        try:
                           pronto = string.replace(response.split('\n')[1],' ',', 0x')
                           pronto = "0x" + pronto
                           prontoLen = len(pronto.split(','))
                           if (DEBUGPRONTO):
                                print "Pronto generated for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                                print "Generated pronto is: " + str(pronto)
                        except Exception as e:
                            if (DEBUG | LOG):
                                print "###### Pronto generation error for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[13]: " +str(e)

                        ############## creating json format ##############################
                        try:
                            jsonData= json.dumps({"remoteName":remoteFile,"protocol": protocolName,"device": deviceNo,"subdevice": subdeviceNo,"key_code": keyCode,"key_name": keyName,"code_len": prontoLen,"pronto_code": pronto })
                            if(DEBUGJSON):
                                print "Json created for key: "+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                                print "Created json is: " + str(jsonData)
                        except Exception as e:
                            if (DEBUG | LOG):
                                 print "###### Json creation error for key"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)+",ERROR[13]: " +str(e)

                        ############# writing to file ##################################
                        #if DBCREAT:
                        try:
                            print "json file name: "+ str(jsonLineNo)
                           # jsonFileHandler.write(jsonData)
                            #if(jsonLineNo<len(keyCodeArray)-1):

                               #jsonFileHandler.write(",\n")
                            jsonLineNo += 1
                            if(DEBUG):
                                print "Json written succesfully in file:"+ str(jsonFileName)+"for key :"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)
                        except Exception as e:
                            if (DEBUG | LOG):
                                print "##### Json writting error in file:"+ str(jsonFileName)+"for key :"+ str(keyName)+ ", for remote file: "+str(remoteFile)+ ", for remote: " + str(remote) + ", for company: " + str(company)

    except Exception as e:
        if (DEBUG | LOG):
            print   "###### Folder opening error for comapany : " + str(company)+", ERROR[]: "+ str(e)

if __name__ == '__main__':
    main()