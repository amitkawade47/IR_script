
        f= open('/Irdb_csv/','r')
        if (DEBUG):
            print "File" + str(csvFileName)+  "opend."


        for i in range (50):
            read = f.readline()
            if not read :
                break
            read =  read.split(",")
            keyName = read[0]
            #functionNo = read[4].strip()
            if(i > 0):
                functionArray.append(read[4].strip())
                keyArray.append(read[0])
            if(i == 1):
                protocolName = read[1]
                deviceNo = read[2]
                subdeviceNo = read[3]
            i= i+1
            read = ""
    f.close()
    print protocolName
    print deviceNo
    print subdeviceNo
    print functionArray
    print keyArray
