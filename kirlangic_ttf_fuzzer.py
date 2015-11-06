#!/usr/bin/python
#-*- coding: utf-8 -*-
# 2015
# SIGNALSEC

# Visit github.com/signalsec for latest updates
# Java/Silverlight Generator Scripts located in Github page
# thanks to lclee_vx for bug fix

import argparse
import logging

from BeautifulSoup import BeautifulStoneSoup as soup
from fpdf import FPDF
from glob import glob
from os import curdir, mkdir, listdir, remove, rename
from shutil import make_archive, move 
from struct import pack, unpack
from sys import argv, exit, stdout
from time import sleep

#########################################################################
#                                 CONFIG
#########################################################################

AUTHORS       = "SIGNALSEC"
NAME          = "Kirlangic TTF Fuzzer"
VERSION       = "1.2"

def InitParams():
    global args
    parser = argparse.ArgumentParser(
                formatter_class = argparse.RawDescriptionHelpFormatter,
                description     = "%s - v%s\n%s\n" %(NAME, VERSION, AUTHORS),
                epilog          = """

Usage:

./%(prog)s -i ttfFile.ttf

    """)

    if len(argv) == 1:      
        parser.print_help()
        exit(1)

    parser.add_argument("-i", default=True, metavar="", help="ttf input")
    parser.add_argument("-fuzzvalue", default="ff", metavar="ff", help="fuzz value")
    parser.add_argument("-o", default="fuzzedfiles", metavar="fuzzedfiles", help="fuzzed files output dir")
    parser.add_argument("-od", default="fuzzeddocx/", metavar="fuzzeddocx", help="docx output dir")
    parser.add_argument("-op", default="fuzzedpdf/", metavar="fuzzedpdf", help="pdf output dir")
    parser.add_argument("-m", default=10000, metavar="10000", help="max lenght of table")
    parser.add_argument("-docx", metavar="", help="create docx files", const=True, action="store_const")
    parser.add_argument("-pdf", metavar="", help="create pdf files", const=True, action="store_const")  

    args = parser.parse_args()

def InitLogger():
    logger = logging.getLogger("Kirlangic")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger

#########################################################################
#                                 FUZZER
#########################################################################
def createTTFFile(origTTF, tableData, fOffset, table, tOffset):
    dName = "table" + str(table-1) + "offset" + str(fOffset) + ".ttf" 

    if args.o not in listdir(curdir):
       mkdir(args.o)

    FILE = open(args.o + "/" + dName, "wb")
    #Write original TTF

    FILE.write(origTTF)
    #Get current checksum.. (Ulan ceylan.)
    oChecksum = retChecksum(origTTF, table)
    #Check if we need to adjust table lenght (When len(table) % 4 != 0)
    fourFix = False
    if len(tableData) % 4 != 0:
        fourFix        = True
        fixedSize      = ((len(tableData) + 3 ) & ~3) - len(tableData)
        tDataFourFixed = tableData + origTTF[int(retOffsetLenght(origTTF, table)[0], 16) + int(retOffsetLenght(origTTF, table)[1], 16):\
                                             int(retOffsetLenght(origTTF, table)[0], 16) + int(retOffsetLenght(origTTF, table)[1], 16)+fixedSize]

    #Four fixed, normal table
    if fourFix:
        calcChecksum = calcNewTableChecksum(tDataFourFixed, oChecksum)
    #No need four fix, normal table
    else:
        calcChecksum = calcNewTableChecksum(tableData, oChecksum)
    
    #Do we need to update checksum ?
    if calcChecksum[0] and table != headTableNumber:
        #Yes, update it
        FILE.seek(table*12+table*4)        
        calcChecksum2 = calcChecksum[1]
        if len(calcChecksum2) < 8:
            #Fill empty bytes with zero
            calcChecksum2 = ("0" * (8 - len(calcChecksum2))) + calcChecksum2     

        FILE.write(calcChecksum2.decode("hex"))

    #Write fuzzed table
    FILE.seek(0)
    FILE.seek(tOffset)
    FILE.write(tableData)
    FILE.close()

    tFILE = open(args.o + "/" + dName, "rb")
    #Update Head checksum
    HeadChecksum = calcHeadChecksum(tFILE, headTableNumber)       
    HeadChecksum2 = HeadChecksum[1] #HEAD's checkSumAdjustment
    HeadChecksum1 = HeadChecksum[2] #HEAD's Checksum
    HeadOffset3 = HeadChecksum[3] #HEAD's offset

    if len(HeadChecksum2) < 8:
        HeadChecksum2 = ("0" * (8 - len(HeadChecksum2))) + HeadChecksum2
    if len(HeadChecksum1) < 8:
        HeadChecksum1 = ("0" * (8 - len(HeadChecksum1))) + HeadChecksum1

    #Do we need to update head checksum?
    if HeadChecksum[0]:
        #Yes, read file for checksum update
        tFILE.seek(0)    
        temp = list(tFILE.read())    
        tFILE.close()
        
        #Update checksum and write it to file          
        #temp[headTableNumber*12+headTableNumber*4:headTableNumber*12+headTableNumber*4+4] = HeadChecksum2.decode("hex")
        temp[headTableNumber*12+headTableNumber*4:headTableNumber*12+headTableNumber*4+4] = HeadChecksum1.decode("hex") #update checkSumAdjustment
        temp[HeadOffset3 + 8:HeadOffset3 + 12] = HeadChecksum2.decode("hex") #update checksum

        FILE = open(args.o + "/" + dName, "wb")
        FILE.write("".join(temp))
        FILE.close()
    else:
        tFILE.close()

def enumTables(fileN):
    return int(fileN[4:6].encode("hex"), 16)

def retChecksum(fileN, i):
    return fileN[i*12+i*4:i*12+i*4+4].encode("hex")

def retOffsetLenght(fileN, i):
    return fileN[i*12+i*4+4:i*12+i*4+8].encode("hex"), \
           fileN[i*12+i*4+8:i*12+i*4+12].encode("hex")

def retTableName(fileN, i):
    return fileN[i*12+i*4-4:i*12+i*4]

def InitDataToFuzz(data, n):
    while data:
        yield data[:n]
        data = data[n:]

def calcNewTableChecksum(tableD, origChecksum):
    totalData = 0

    for i in range(0, len(tableD), 4):
        try: 
            data = unpack(">I", tableD[i:i+4] ) [0]
        except Exception, error:
            print "\n\nFAULT: ", error
            print "len(tableData): {0}, must be >= {1}".format(len(tableD), (len(tableD) + 3 ) & ~3)
            exit(0)
        
        totalData += data
    
    finalData    = 0xffffffff & totalData
    finalDataHex = "".join("%x")%(finalData)

    if finalData != int(origChecksum, 16):
        #Need to update checksum
        LOGGER.debug("\n\tChecksum error, calculated: {0} - original: {1}".format(finalDataHex, origChecksum))
        return True, finalDataHex

    #No need to update checksum
    return False, finalDataHex

def calcHeadChecksum(fHandle, tableN):
    #Get table info
    fread= fHandle.read()
    hInfo = retOffsetLenght(fread, tableN)
    hTable = fread[int(hInfo[0], 16):int(hInfo[0],16)+int(hInfo[1],16)+2]
    oChecksum = retChecksum(fread, tableN)

    #Firstly calculate head table's checksum
    totalData = 0
    hTableCalc = len(hTable) % 4
    hTable = hTable[0:(len(hTable)-hTableCalc)]
    for i in range(0, len(hTable), 4):
        if i == 8:
            data = 0
            checkSumAdjustement = unpack(">I", hTable[i:i+4] ) [0]
        else:
            data = unpack(">I", hTable[i:i+4] ) [0]
			#data = unpack(">I", hTable[i:i+4])[0]
        totalData += data

    finalData    = 0xffffffff & totalData
    finalDataHex = "".join("%x")%(finalData)
    headChecksumUpdate = finalDataHex #backup the HEAD checksum 

    if finalData != int(oChecksum, 16):
        LOGGER.debug("\n\tChecksum error, calculated: {0} - original: {1}".format(finalDataHex, oChecksum))

    #Now, calculate entire font checksum
    fHandle.seek(0, 2)
    endFile = fHandle.tell()
    fHandle.seek(0)

    totalData = 0
    tempFont = fHandle.read(endFile)
    offset   = int(retOffsetLenght(tempFont, tableN)[0], 16)
    headOffset = offset  #HEAD checksum
    #Set checkSumAdjustement to 0 in temporary font
    tempFont = tempFont[:offset + 8] + pack(">I", 0) + tempFont[offset + 12:]
    #Set the updated 'HEAD' checksum, calculate when set checkSumAdjustement=0
    headChecksumUpdateOffset = ((tableN-1)*0x10)+0xc
    tempFont = tempFont[:headChecksumUpdateOffset+4] + pack(">I", finalData) + tempFont[headChecksumUpdateOffset+8:]

    #NEED FIX WHEN len(TEMPFONT) % 4 != 0
    if len(tempFont) % 4 != 0:
        fixedSize = ((len(tempFont) + 3 ) & ~3) - len(tempFont)
        tempFont  = tempFont + (fixedSize * "0")

    for i in range(0, len(tempFont), 4):
        data      = unpack(">I", tempFont[i:i+4] ) [0]
        totalData += data

    finalData = totalData & 0xffffffff 
    finalData = (0xb1b0afba - finalData) & 0xffffffff 
    
    #Hex convert
    finalDataHex           = "".join("%x")%(finalData)
    checkSumAdjustementHex = "".join("%x")%(checkSumAdjustement)
    if finalData != checkSumAdjustementHex:
        LOGGER.debug("\n\tMain checksum error, calculated: {0} - original: {1}".format(finalDataHex, checkSumAdjustementHex))
        return True, finalDataHex, headChecksumUpdate, headOffset

    return False, finalDataHex



def letsFuzzTable(tFile, tOffset, tLenght, tableNo):
    start, add = 0, 0
    tableData  = tFile[tOffset:tOffset+tLenght]
    tableData2 = tableData.encode("hex")
    #returnList = []
    #???
    
    if len(args.fuzzvalue) == 4: add = 1
    tLenghtL = ((tLenght / len(args.fuzzvalue)) *2) + add
  
    while start < tLenghtL:
        tableDataList = list(InitDataToFuzz(tableData2, len(args.fuzzvalue)))

        #Fuzz table
        try: tableDataList[start] = args.fuzzvalue
        except: return
        #returnList.append(tableDataList)

        #Create fuzzed TTF
        tableFuzzedData = "".join(tableDataList).decode("hex")
        createTTFFile(tFile, tableFuzzedData, start, tableNo, tOffset)
        start += 1

    #Update Checksum, create fuzzed ttf
    #for fuzzOffset in range(len(returnList)):
        #fuzzedTable = "".join(returnList[fuzzOffset]).decode("hex")
        #createTTFFile(tFile, fuzzedTable, fuzzOffset, tableNo, tOffset)

def InitFuzz(RTTF, tNumbers):
    global headTableNumber

    print
    print "No  Table\tChecksum\tOffset\t Lenght"
    print "-----------------------------------------------"

    for i in range(1, tNumbers):
        print "%.2d "%(i-1), retTableName(RTTF, i), "\t", retChecksum(RTTF, i), "\t", \
                            retOffsetLenght(RTTF, i)[0], retOffsetLenght(RTTF, i)[1]

        if retTableName(RTTF, i) == "head":
            headTableNumber = i

    print "\n\n----------- Fuzzing starting ------------"
    print "Max Table Lenght:", args.m
    print

    for i in range(1, tNumbers):
        stdout.write(("[*] Table {0} fuzzing...").format(i-1))

        #First check table lenght (beep if fail & skip it)
        if int(retOffsetLenght(RTTF, i)[1], 16) > int(args.m):
            print " SKIPPED! Lenght: {0}\a".format(int(retOffsetLenght(RTTF, i)[1], 16))
            continue

        #Fuzz table
        letsFuzzTable(RTTF, int(retOffsetLenght(RTTF, i)[0], 16), \
                            int(retOffsetLenght(RTTF, i)[1], 16), i)


        stdout.write(" OK!\n")
        #Delay
        sleep(0.2)


    print
    print "[!] Total {0} fuzzed TTF found in fuzzed ttf folder.".format(len(glob(args.o + "/*.ttf")))
    print

#########################################################################
#                          DOCX GENERATOR
#########################################################################
def InitDocx(ttfFolder):
    print "\n----------- Docx generating ------------"

    print "Font info:"
    gKey = findFontGUID("docTemplate/word/fontTable.xml")
    print "[*] Fuzzed docx genarating..."

    pBar = (["\\", "|", "/", "-"])
    i = 1
    j = 0
    for tFile in listdir(ttfFolder):      
        if tFile.endswith(".ttf"):      
            createOdttf(tFile, gKey)
            createDocx(tFile)

            stdout.write("\r[{0}] Total {1} fuzzed docx generated.".format(pBar[j], i))

            i +=1
            j +=1
            if j == 4:
                j = 0

def findFontGUID(fontTable):
    xmlStr = open(fontTable, "r").read()
    xml    = soup(xmlStr)

    for i, k in enumerate(xml.findAll("w:font")):
        fName = k["w:name"]
        x     = soup(str(k))

        try:
            fontKey =  x.findAll("w:embedregular")[0]["w:fontkey"]
            fontKey = "".join(fontKey[1:-1].split("-"))
        except:
            continue

    print "\tFont: {0}\n\tKey : {1}".format(fName, fontKey)
    print

    return fontKey

def createOdttf(ttfFont, fKey):
    #Delete old ODTTF
    try:
        remove("font1.odttf")
    except Exception:
        #No old odttf, skip
        pass

    fontKey   = fKey.decode("hex")
    origFontR = open(args.o + "/" + ttfFont, "rb").read()
    origFontL = [ord(x) for x in origFontR]

    #Create new ODTTF
    for i in range(16):
        origFontL[i]    = ord(origFontR[i]) ^ ord(fontKey[15-i])
        origFontL[i+16] = ord(origFontR[i+16]) ^ ord(fontKey[15-i])

    origFontL = "".join([ "%c" % sla for sla in origFontL])
    open("font1.odttf", "wb").write(origFontL)

def createDocx(tFile):
    try:
        remove("docTemplate/word/fonts/font1.odttf")
    except Exception:
        #No old odttf in docx, skip
        pass

    #Move fuzzed odttf to docx template
    move("font1.odttf", "docTemplate/word/fonts")

    #Set fuzzed docx name
    sDfile = tFile.split(".ttf")[0]

    #Create Docx under fuzzeddocx
    make_archive(args.od + "/" + sDfile, "zip", "docTemplate")
    try:
        rename(args.od + sDfile + ".zip", args.od + sDfile + ".docx")
    except WindowsError:
        #Already exist, remove it first
        remove(args.od + sDfile + ".docx")
        rename(args.od + sDfile + ".zip", args.od + sDfile + ".docx")

#########################################################################
#                          PDF GENERATOR
#########################################################################
def InitPDF(ttfFolder):
    print "\n----------- PDF generating ------------"
    print "[*] Fuzzed pdf genarating..."

    pBar = (["\\", "|", "/", "-"])
    i = 1
    j = 0
    for tFile in sorted(listdir(ttfFolder)):
        if tFile.endswith(".ttf"):      
            createPDF(tFile)

            stdout.write("\r[{0}] Total {1} fuzzed pdf generated.".format(pBar[j], i))

            i +=1
            j +=1
            if j == 4:
                j = 0

def createPDF(tFile):
	#Create PDF output dir if not exist
    if args.op.split("/")[0] not in listdir(curdir):
    	mkdir(args.op)

    #Set fuzzed pdf name
    sPfile = tFile.split(".ttf")[0]
    tempPDF = FPDF()
    #Add our fuzzed ttf into PDF
    try: tempPDF.add_font(sPfile, "", args.o + "/" + tFile, uni=True)
    except: return 
    tempPDF.set_font(sPfile, "", 16)

    #Create blank page and fill it with data
    tempPDF.add_page()
    tempPDF.cell(40, 10, "PDF TEST FILE")

    #Create fuzzed PDF
    try: tempPDF.output(args.op + sPfile + ".pdf", "F")
    except: return 
    
    tempPDF.close()

#########################################################################
#                             CRASH TEST MAIN
#########################################################################
def InitCrashTest(docxFolder):
    print
    print "\n--------- Crash test starting ----------"
    #TODO

#########################################################################
#                             Kirlangic MAIN
#########################################################################
if __name__ == "__main__":
    InitParams()
    LOGGER = InitLogger()

    if args.i != True:
        try:
            ReadedTTF = open(args.i, "rb").read()
        except Exception, error:
            print "[!] Error :", error
            exit(0)

        numTables = enumTables(ReadedTTF)
        print "[!] Number of tables:", numTables

        #Generate fuzzed TTFs
        InitFuzz(ReadedTTF, numTables+1) 
        sleep(1)
    else:
        print "TTF fuzzing skiped."

    try:
        if args.docx == True:
            InitDocx(args.o)
            sleep(1)

        elif args.pdf == True:
            InitPDF(args.o)
            sleep(1)

        else:
            print "[!] Where is your method -_-"
            exit(1)

        #Start to test fuzzed docx files
        InitCrashTest(args.od)

    except KeyboardInterrupt:
        print "\n\n[!] Terminated by the user...\n"
        exit(0)
