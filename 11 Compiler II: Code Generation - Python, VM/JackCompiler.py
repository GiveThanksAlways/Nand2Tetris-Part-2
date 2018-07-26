from Tokenizer import tokenType,tokenWrap,insideAstring
from Parser import Parser
import glob
import sys
import os
from pathlib import Path

nonTerminals = ['class','classVarDec','subroutineDec','parameterList','subroutineBody','varDec','statements','whileStatement','ifStatement','returnStatement','letStatement','doStatement','expression','term','expressionList']
from SymbolTable import SymbolTable,Node,LinkedList

parserSymbolTable = SymbolTable()


# first time to get the OS classes

#for folderName, subfolders, filenames in os.walk(os.getcwd()):
  #print('The current folder is ' + folderName)


  #for subfolder in subfolders:
    #print('SUBFOLDER OF ' + folderName + ': ' + subfolder)
    #2+2
import sys
import os
import glob
from pathlib import Path

# just parse the OS directory first
directoryName = "OS"
folderName = str(Path(directoryName).resolve())
# if the input is a directory, then we change to that directory
os.chdir(os.path.realpath(directoryName))

# now that the cwd is correct, we get the filename
#XMLFileName = str(os.getcwd())
#XMLFileName = XMLFileName.rpartition("/")[2]
items = os.listdir(".") # gets all of the files in the directory
onlyOS = []
for item in items:
    if(item.endswith(".jack")):
        onlyOS.append(item)

for filename in onlyOS:

    #print(filename.split('.')[-1])
    #print(folderName.split('.'))
    #print(folderName.split('.') )
    #print(filename)
    #justFoldername = folderName.split('/')[-1]
    #if filename.split('.')[-1] == 'jack' and justFoldername == "Sqasdfasduare":
      #print('FILE INSIDE ' + folderName + ': '+ filename)
      #print(filename)

    #for filename in glob.glob('*.jack'):

      #print(os.getcwd())
      #print(filename)
      content = []
      #print(filename)
      #print(folderName)
      #print(os.getcwd())
      fileInDirectory = os.path.join(os.getcwd(),filename)
      #print(fileInDirectory)
      #print(fileInDirectory)
      with open(fileInDirectory) as f:
          for line in f:
              #if( not (line.startswith("/**") or line.startswith("*") or line.startswith("//") or line.startswith("*/")) ):
                #if any of those are true, then it is a comment so we ignore it
              line = line.lstrip(' ') # this will take away the white space
              if( not (line.startswith("//") or line.startswith("/**") or line.startswith("*") or line.startswith("*/"))):
                #print('hit')
                #print(line)
                # takes out the // at the end of the code
                line = line.split('//', 1)[0]
                #line = line.split('/*')[0]
                line = line.rstrip()
                # take out the more than one line comments with *
                #a = list(line)
                #if len(a) > 2:
                  #if a[0] ==' ' and a[1] == '*':
                    #print(line)
                    #line = line.split('*')[0]
                    #line = line.rstrip()
                    #print(line)
                content.append(line)

      content = [x.strip() for x in content]
      content[:] = [item for item in content if item != ''] # takes out the empty lines
      # output string is for the xml file
      output_string = os.path.join(folderName, str(filename[:filename.index('.')]))
      # output token string is for just the tokens xml
      output_Token_string = str(filename[:filename.index('.')])+'Token'+'.xml'
      output = open(os.path.join(folderName,output_Token_string) ,'w')
      tokenArray = []
      tokenToPrint=[]
      stringcounter = 0
      for item in content:
        #print(item)
        for letter in item:
          #print(letter)

          # use mod (%) to tell if in string or not
          if letter == '"':
            stringcounter += 1

          if insideAstring(stringcounter):
            # we are still in a string so just print everything until end of string
            tokenArray.append(letter) # take all values till " sign
          elif letter != ' ':
            #print(letter)

            if tokenType(letter) == 'symbol':
              tokenToPrint.append(''.join(tokenArray))
              tokenArray = []
              tokenArray.append(letter)
              #print(''.join(tokenArray))
              tokenToPrint.append(''.join(tokenArray))
              tokenArray = []
            else:
              tokenArray.append(letter)

          else:
            #print(''.join(tokenArray))
            tokenToPrint.append(''.join(tokenArray))
            tokenArray = []



      tokenToPrint = [x.strip() for x in tokenToPrint]
      tokenToPrint[:] = [item for item in tokenToPrint if item != '']
      #print(tokenToPrint)

      # Take tokens and wrap in XML

      XMLTokensList = ['<tokens>']
      for token in tokenToPrint:
        tokenWrap(XMLTokensList,token)
        #print(token)
      XMLTokensList.append('</tokens>')

      # take the xml wrapped tokens and output to output file
      for item in XMLTokensList:
        #print(item)
        output.write(item)
        output.write('\n')
      output.close()
      #print(XMLTokensList)
      XMLTokensList.clear()


      # Now Parse the tokens
      #print(output_Token_string,output_string)



      da_output = Parser(os.path.join(folderName,output_Token_string),output_string,parserSymbolTable)
      #parserSymbolTable.viewTableCST()


























# now we parse the input now that we have the OS clases in the symboltable


directoryName = sys.argv[1]
daRealpath = str(Path(sys.argv[1]).resolve())
#print(directoryName)
#print(os.getcwd()) # was in OS directory
os.chdir("..") # go up one to normal directory
#print(os.getcwd()) # now we are in normal directory

# if the input ends with .jack then the input is a file. So change the directory to the directory of that file
if(sys.argv[1].endswith(".jack")):
    daRealpath = str(daRealpath.rpartition("/")[0])
    os.chdir(daRealpath)
else:
    # if the input is a directory, then we change to that directory
    os.chdir(os.path.realpath(directoryName))
# first loop to get the symbol table of all classes with all functions

for folderName, subfolders, filenames in os.walk(os.getcwd()):
  #print('The current folder is ' + folderName)

  for subfolder in subfolders:
    #print('SUBFOLDER OF ' + folderName + ': ' + subfolder)
    2+2

  for filename in filenames:

    #print(filename.split('.')[-1])
    #print(folderName.split('.'))
    #print(folderName.split('.') )
    if filename.split('.')[-1] == 'jack':
      #print('FILE INSIDE ' + folderName + ': '+ filename)
      #print(filename)

    #for filename in glob.glob('*.jack'):

      #print(os.getcwd())
      #print(filename)
      content = []
      #print(filename)
      #print(folderName)
      #print(os.getcwd())
      fileInDirectory = os.path.join(folderName,filename)
      #print(fileInDirectory)
      #print(fileInDirectory)
      with open(fileInDirectory) as f:
          for line in f:
              #if( not (line.startswith("/**") or line.startswith("*") or line.startswith("//") or line.startswith("*/")) ):
                #if any of those are true, then it is a comment so we ignore it
              line = line.lstrip(' ') # this will take away the white space
              if( not (line.startswith("//") or line.startswith("/**") or line.startswith("*") or line.startswith("*/"))):
                #print('hit')
                #print(line)
                # takes out the // at the end of the code
                line = line.split('//', 1)[0]
                #line = line.split('/*')[0]
                line = line.rstrip()
                # take out the more than one line comments with *
                #a = list(line)
                #if len(a) > 2:
                  #if a[0] ==' ' and a[1] == '*':
                    #print(line)
                    #line = line.split('*')[0]
                    #line = line.rstrip()
                    #print(line)
                content.append(line)

      content = [x.strip() for x in content]
      content[:] = [item for item in content if item != ''] # takes out the empty lines
      # output string is for the xml file
      output_string = os.path.join(folderName, str(filename[:filename.index('.')]))
      # output token string is for just the tokens xml
      output_Token_string = str(filename[:filename.index('.')])+'Token'+'.xml'
      output = open(os.path.join(folderName,output_Token_string) ,'w')
      tokenArray = []
      tokenToPrint=[]
      stringcounter = 0
      for item in content:
        #print(item)
        for letter in item:
          #print(letter)

          # use mod (%) to tell if in string or not
          if letter == '"':
            stringcounter += 1

          if insideAstring(stringcounter):
            # we are still in a string so just print everything until end of string
            tokenArray.append(letter) # take all values till " sign
          elif letter != ' ':
            #print(letter)

            if tokenType(letter) == 'symbol':
              tokenToPrint.append(''.join(tokenArray))
              tokenArray = []
              tokenArray.append(letter)
              #print(''.join(tokenArray))
              tokenToPrint.append(''.join(tokenArray))
              tokenArray = []
            else:
              tokenArray.append(letter)

          else:
            #print(''.join(tokenArray))
            tokenToPrint.append(''.join(tokenArray))
            tokenArray = []



      tokenToPrint = [x.strip() for x in tokenToPrint]
      tokenToPrint[:] = [item for item in tokenToPrint if item != '']
      #print(tokenToPrint)

      # Take tokens and wrap in XML

      XMLTokensList = ['<tokens>']
      for token in tokenToPrint:
        tokenWrap(XMLTokensList,token)
        #print(token)
      XMLTokensList.append('</tokens>')

      # take the xml wrapped tokens and output to output file
      for item in XMLTokensList:
        #print(item)
        output.write(item)
        output.write('\n')
      output.close()
      #print(XMLTokensList)
      XMLTokensList.clear()


      # Now Parse the tokens
      #print(output_Token_string,output_string)



      da_output = Parser(os.path.join(folderName,output_Token_string),output_string,parserSymbolTable)
      #parserSymbolTable.viewTableCST()


#parserSymbolTable.viewTableCST()
# 2nd loop that can now parse the data with a full symbol table of everyfunction in every
for folderName, subfolders, filenames in os.walk(os.getcwd()):
  #print('The current folder is ' + folderName)

  for subfolder in subfolders:
    #print('SUBFOLDER OF ' + folderName + ': ' + subfolder)
    2+2

  for filename in filenames:
    #print(filename.split('.')[-1])
    #print(folderName.split('.'))
    #print(folderName.split('.') )
    if filename.split('.')[-1] == 'xml' and filename.find("Token") != -1:   # old code --- > and filename == "MainToken.xml":
      #print(filename.find("Token") != -1)

      output_string = os.path.join(folderName, str(filename[:filename.index('Token')]))

      da_output = Parser(os.path.join(folderName,filename),output_string,parserSymbolTable)
      #parserSymbolTable.viewTableCST()
