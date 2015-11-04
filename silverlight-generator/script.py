import os
import sys
from PIL import ImageFont
import xml.etree.ElementTree as ET
import shutil
import time

fontPath = sys.argv[1]
outputPath = sys.argv[2]

def getFileList(path):
	global fileList
	fileList = []
	for root, dirnames, filenames in os.walk(path):
		# store path to all files.
		for filename in filenames:
			fileList.append((filename, r"%s" % (os.path.join(root, filename))))

getFileList(fontPath)

def getFontName(fontFile):
	f = ImageFont.truetype(fontFile, 1)
	try:
		name = f.font.family #+ " " + f.font.style
		return name
	except (TypeError):
		pass

def MainPageXaml(fontFileName, fontFamilyName):
	with open("SilverlightApplication1\Master.xaml", 'r+') as rFile:
		readData = rFile.read()
		
		readData = readData.replace("""FontFamily="dexter.ttf#DexterC\"""",
									"""FontFamily="%s#%s\"""" % (fontFileName, fontFamilyName))
		with open("SilverlightApplication1\MainPage.xaml", 'w') as wFile:
			wFile.write(readData)
			wFile.close()

def CSProj(fileName):
	document = ET.parse('SilverlightApplication1\SilverlightApplication1.csproj')
	root = document.getroot()
	ET.register_namespace('',"http://schemas.microsoft.com/developer/msbuild/2003")

	for i in root.getchildren():
		for z in i.getchildren():
			if z.tag == '{http://schemas.microsoft.com/developer/msbuild/2003}Resource':
				z.attrib['Include'] = str(fileName)
				document.write('SilverlightApplication1\SilverlightApplication1.csproj')

def MSBuild():
	os.system("MSBuild.exe SilverlightApplication1.sln /p:Configuration=Release")
 
def run():
	for f in fileList:
		filename = f[0]
		filepath = f[1]
		fontFamily = getFontName(f[1])
		shutil.copy(filepath, 'SilverlightApplication1')
		MainPageXaml(filename, fontFamily)
		CSProj(filename)
		MSBuild()
		shutil.copy('SilverlightApplication1\Bin\Release\SilverlightApplication1.xap', '%s/%s.xap' % (outputPath, os.path.splitext(filename)[0]))
		shutil.rmtree('SilverlightApplication1\Bin')
		shutil.rmtree('SilverlightApplication1\obj')
		os.remove("SilverlightApplication1\MainPage.xaml")
		os.remove("SilverlightApplication1\%s" % (filename))
		time.sleep(1)


run()