import os,sys,time

ttffolder = "fuzzedjava/fuzzedttf"

f = open("FuzzJavaTTF.java", 'r')
filedata = f.read()
f.close()

for fuzzedTTf in sorted(os.listdir(ttffolder)):
    if fuzzedTTf.endswith(".ttf"):
        casename = fuzzedTTf.split(".")[0]
        newttf  =  "/fuzzedttf/" + fuzzedTTf

        newdata = filedata.replace("Dexter.ttf", newttf)
        #newdata = newdata.replace("Dexter", fuzzedTTf.split(".")[0])
        newdata = newdata.replace("FuzzJavaTTF", casename)

	    #dosyayi olustur
        filename = "fuzzedjava/" + casename + ".java"
        f = open(filename, 'w')
        f.write(newdata)
        f.close()
        os.system("javac " + filename )

#clean java source files
for remJava in os.listdir("fuzzedjava"):
    if remJava.endswith(".java"):
	    os.remove("fuzzedjava/" + remJava)

