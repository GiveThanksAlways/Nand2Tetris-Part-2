from Tokenizer import tokenType,tokenWrap,insideAstring

from Parser import Parser

import glob

import os

nonTerminals = ['class','classVarDec','subroutineDec','parameterList','subroutineBody','varDec','statements','whileStatement','ifStatement','returnStatement','letStatement','doStatement','expression','term','expressionList']

from SymbolTable import SymbolTable,Node,LinkedList
parserSymbolTable = SymbolTable()
# OS and other functions
#defineSubroutineTracker(self.subroutineName,'method' ,self.className,self.subroutineVoid)
parserSymbolTable.defineSubroutineTracker('deAlloc','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('keyPressed','0','OS',False) # not void
parserSymbolTable.defineSubroutineTracker('wait','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('moveCursor','2','OS',True) # void
parserSymbolTable.defineSubroutineTracker('clearScreen','0','OS',True) # void
# methods have k+1 because the plust one is the object 'argument 0' or 'pointer 0'
#parserSymbolTable.define('moveUp','1','OS') 
#parserSymbolTable.define('moveDown','1','OS')
#parserSymbolTable.define('moveLeft','1','OS')
#parserSymbolTable.define('moveRight','1','OS')
#parserSymbolTable.define('incSize','1','OS')
#parserSymbolTable.define('dispose','1','OS')
#parserSymbolTable.define('decSize','1','OS')
parserSymbolTable.define('new','0','OS') 
parserSymbolTable.defineSubroutineTracker('setColor','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('drawRectangle','4','OS',True) # void
parserSymbolTable.defineSubroutineTracker('printInt','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('println','0','OS',True) # void
parserSymbolTable.defineSubroutineTracker('printString','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('readInt','1','OS',True) # void

# functions not in OS
parserSymbolTable.defineSubroutineTracker('abs','1','OS',False) # void
parserSymbolTable.defineSubroutineTracker('show','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('draw','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('newInstance','0','OS',True) # void
parserSymbolTable.defineSubroutineTracker('getInstance','0','OS',False) # void
parserSymbolTable.defineSubroutineTracker('run','1','OS',True) # void
parserSymbolTable.defineSubroutineTracker('moveBall','1','OS',True) # void
#parserSymbolTable.defineSubroutineTracker('move','1','OS',True) # void


#parserSymbolTable.define(daname,datype,dakind)





for folderName, subfolders, filenames in os.walk('/home/runner'):
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
      output_string = os.path.join(folderName, str(filename[:filename.index('.')]))
      #str(filename[:filename.index('.')])
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

parserSymbolTable.viewTableCST()

    






  