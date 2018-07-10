from Tokenizer import tokenType,tokenWrap,insideAstring
'''
from Parser import compileClass,compileClassVarDec,compileSubroutine,compileParameterList,compileVarDec,compileStatements,compileDo,compileLet,compileWhile,compileReturn,compileIf,compileExpression, compileTerm,compileExpressionList
'''

from Parser import Parser

nonTerminals = ['class','classVarDec','subroutineDec','parameterList','subroutineBody','varDec','statements','whileStatement','ifStatement','returnStatement','letStatement','doStatement','expression','term','expressionList']


import glob

for filename in glob.glob('*.jack'):
  
  content = []
  #print(filename)
  with open(filename) as f:
      for line in f:
          # takes out the // and /* comments
          line = line.split('//', 1)[0]
          line = line.split('/*')[0]
          line = line.rstrip()
          # take out the more than one line comments with *
          a = list(line)
          if len(a) > 2:
            if a[0] ==' ' and a[1] == '*':
              #print(line)
              line = line.split('*')[0]
              line = line.rstrip()
              #print(line)
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

  
  


  
  
  
  