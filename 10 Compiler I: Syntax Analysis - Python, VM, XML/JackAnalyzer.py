from Tokenizer import tokenType,tokenWrap,insideAstring
'''
from Parser import compileClass,compileClassVarDec,compileSubroutine,compileParameterList,compileVarDec,compileStatements,compileDo,compileLet,compileWhile,compileReturn,compileIf,compileExpression, compileTerm,compileExpressionList
'''

from Parser import Parser

nonTerminals = ['class','classVarDec','subroutineDec','parameterList','subroutineBody','varDec','statements','whileStatement','ifStatement','returnStatement','letStatement','doStatement','expression','term','expressionList']

import sys
import os
import glob
from pathlib import Path
directoryName = sys.argv[1]

daRealpath = str(Path(sys.argv[1]).resolve())

# if the input ends with .jack then the input is a file. So change the directory to the directory of that file
if(sys.argv[1].endswith(".jack")):
    daRealpath = str(daRealpath.rpartition("/")[0])
    os.chdir(daRealpath)
else:
    # if the input is a directory, then we change to that directory
    os.chdir(os.path.realpath(directoryName))

# now that the cwd is correct, we get the filename
XMLFileName = str(os.getcwd())
XMLFileName = XMLFileName.rpartition("/")[2]
items = os.listdir(".") # gets all of the files in the directory
onlyjack = []
for item in items:
    if(item.endswith(".jack")):
        onlyjack.append(item)

#output = open(XMLFileName+ ".asm",'w')

#for filename in glob.glob('*.vm'):
for filename in onlyjack:

  #content = []
#import glob

#for filename in glob.glob('*.jack'):

  content = []
  #print(filename)
  with open(filename) as f:
      for line in f:
              line = line.lstrip(' ') # this will take away the leading whitespace
              # check if the line starts with the symbols for comments
              if( not (line.startswith("//") or line.startswith("/**") or line.startswith("*") or line.startswith("*/"))):
                # if there is a trailing comment then remove it
                line = line.split('//', 1)[0]
                line = line.rstrip()
                content.append(line)

  content = [x.strip() for x in content]
  content[:] = [item for item in content if item != '']
  #output = open(filename[:filename.index('.')]+'.xml','w')
  output_string = str(filename[:filename.index('.')])+'.xml'
  output_Token_string = str(filename[:filename.index('.')])+'Token'+'.xml'
  output = open(output_Token_string,'w')
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

  da_output = Parser(output_Token_string,output_string)
