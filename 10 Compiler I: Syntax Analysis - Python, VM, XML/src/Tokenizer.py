keywords = ['class','constructor','function','method','field','static','var','int','char','boolean','void','true','false','null','this','let','do','if','else','while','return']

symbol = ['{','}','(',')','[',']','.',',',';','+','-','*','/','&','|','<','>','=','~']


nonTerminals = ['class','classVarDec','subroutineDec','parameterList','subroutineBody','varDec','statements','whileStatement','ifStatement','returnStatement','letStatement','doStatement','expression','term','expressionList']


def printXMLTag(daList,middle,tags):
  # took the '\t' out to parse now, used to have it first
  
  #XMLList.append('<'+str(tags)+'> '+str(middle)+' </'+str(tags)+'>')
  daList.append('<'+str(tags)+'> '+str(middle)+' </'+str(tags)+'>')
  #print('<'+str(tags)+'>'+str(middle)+'</'+str(tags)+'>')
  
  
def tokenType(input):
  
  for item in keywords:
    if input == item:
      return 'keyword'
      
  L = list(str(input))
  for item in L:
    if item == '"' or item == "'":
      return 'stringConstant'
  
  for item in symbol:
    if input == item:
      return 'symbol'
  
  if input.isdigit():
    return 'integerConstant'
  
  if isinstance(input, str):
    return 'identifier'
    
  
  return 

def insideAstring(daCounter):
  if daCounter % 2 == 1:
    return True 
  else:
    return False

def tokenWrap(daList,input):
  
  #non Terminals
  if tokenType(input)   == 'class':
    2+2
  
  
  #  Terminals  
  if tokenType(input)   == 'symbol':
    if input == '>':
      printXMLTag(daList,'&gt;','symbol')
    elif input == '<':
      printXMLTag(daList,'&lt;','symbol')
    elif input == '&':
      printXMLTag(daList,'&amp;','symbol')
    else:
      printXMLTag(daList,input,'symbol')
  elif tokenType(input) == 'keyword':
    printXMLTag(daList,input,'keyword')
  elif tokenType(input) == 'stringConstant':
    string1 = str(input)
    printXMLTag(daList,string1.strip('"'),'stringConstant')
  elif tokenType(input) == 'integerConstant':
    printXMLTag(daList,input,'integerConstant')
  elif tokenType(input) == 'identifier':
    printXMLTag(daList,input,'identifier')
  
  return

