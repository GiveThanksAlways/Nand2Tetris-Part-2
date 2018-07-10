class Parser:
  def __init__(self, parserInput, parserOutput):
    
    self.tTp = [] #tokens to parse array aka tTp
    self.tTpcopy = [] #copy to help remove stuff
    self.tokenCounter = 0
    self.indent = 0

    # open the input.xml file made by the tokenizer (full of tokens ready to parse)
    with open(parserInput) as f:
      for line in f:
        self.tTpcopy.append(line)
    
    
    self.tTp = self.tTpcopy[1:-1] # remove unwanted stuff from copy
    self.output1 = open(parserOutput, 'w') #output to write to
    self.currentTokenArr = self.tTp[self.tokenCounter].split(' ')
    self.currentToken = self.tTp[self.tokenCounter] # first token
    self.compileClass() # start compiling

    self.output1.close() # close the file when done
    
# compile the class
  def compileClass(self):
    self.output1.write('<class>'+'\n')
    self.increaseIndent()
    self.writeAdv() 
    self.writeAdv()
    self.writeAdv()


    self.compileClassVarDec()
    self.compileSubroutine()
    self.outIndent()
    self.output1.write(self.currentToken)
    self.output1.write('</class>'+'\n')
    
    return 

  def compileClassVarDec(self):
    

    if str(self.currentToken) == '<keyword> field </keyword>\n' or str(self.currentToken) == '<keyword> static </keyword>\n':
      self.outIndent()
      self.output1.write('<classVarDec>\n')
      self.increaseIndent()
      # while loop takes care of (varName)*
      while str(self.currentToken) != '<symbol> ; </symbol>\n':
        self.writeAdv() 
      self.writeAdv() # ')'

      self.decreaseIndent()
      self.outIndent()
      self.output1.write('</classVarDec>\n')
    # recursion: check if more, then call itself again
    if str(self.currentToken) == '<keyword> field </keyword>\n' or str(self.currentToken) == '<keyword> static </keyword>\n':
      self.compileClassVarDec()
    return

  def compileSubroutine(self):
    self.outIndent()
    self.output1.write('<subroutineDec>\n')
    self.increaseIndent()
    #while str(self.currentToken) != '<symbol> ( </symbol>\n':
    self.writeAdv() # constructor|function|method
    self.writeAdv() # void|type
    self.writeAdv() # subroutineName
    self.writeAdv() # '('
    # if identifier is there, then compileParameterList
    #daToken = str(self.currentToken.split()[0]) # first xml 
    
    #if daToken == '<identifier>':
    self.compileParameterList()
    #else:
    self.writeAdv() # ')' for empty parameterlist

    self.outIndent()
    self.output1.write('<subroutineBody>\n')
    self.increaseIndent()
    self.writeAdv() # print the {

    # compile all of the varDecs first
    if str(self.currentToken) == '<keyword> var </keyword>\n':
      self.compileVarDec()
        
    # enter statements and statements calls itself recursively
    self.compileStatements()  
     
    self.writeAdv() # } ending the subroutineBody
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</subroutineBody>\n')
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</subroutineDec>\n')

    # recusion part
    # check if more subroutines
    # if constructor|function|method then we compileSubroutine
    if str(self.currentToken) == '<keyword> constructor </keyword>\n':
      self.compileSubroutine()
    elif str(self.currentToken) == '<keyword> function </keyword>\n':
      self.compileSubroutine()
    elif str(self.currentToken) == '<keyword> method </keyword>\n':
      self.compileSubroutine()

    return

  def compileParameterList(self):
    self.outIndent()
    self.output1.write('<parameterList>\n')
    self.increaseIndent()

    while str(self.currentToken) != '<symbol> ) </symbol>\n':
      self.writeAdv()
    
    
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</parameterList>\n')
    return

  def compileVarDec(self):
    
    self.outIndent()
    self.output1.write('<varDec>\n')
    self.increaseIndent()

    while str(self.currentToken) != '<symbol> ; </symbol>\n':
      self.writeAdv()
      
    self.writeAdv()
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</varDec>\n')

    if str(self.currentToken) == '<keyword> var </keyword>\n':
      self.compileVarDec()
    return

  def compileStatements(self):
    self.outIndent()
    self.output1.write('<statements>\n')
    self.increaseIndent()

    
    # change to while to check if next guy is statement
    while self.checkStatement():
      if str(self.currentToken) == '<keyword> if </keyword>\n':
        self.compileIf()
      elif str(self.currentToken) == '<keyword> let </keyword>\n':
        self.compileLet()
      elif str(self.currentToken) == '<keyword> while </keyword>\n':
        self.compileWhile()
      elif str(self.currentToken) == '<keyword> do </keyword>\n':
        self.compileDo()
      elif str(self.currentToken) == '<keyword> return </keyword>\n':
        self.compileReturn()

    
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</statements>\n')
    return

  def compileDo(self):
    self.outIndent()
    self.output1.write('<doStatement>\n')
    self.increaseIndent()

    self.writeAdv() # 'do'
    # subroutineCall which is a term, inside of an expression
    
    # LL(2) grammar part. 
    # look ahead one token to see if ( or . for two types of subroutine calls
    lookAhead = self.tTp[self.tokenCounter+1]
    if lookAhead == '<symbol> ( </symbol>\n':
      self.writeAdv() # subroutineName wrapped in identifier tags
      self.writeAdv() # '('
      self.compileExpressionList()
      self.writeAdv() # ')'
      self.writeAdv() # ';'

    else:
      # subroutineName
      self.writeAdv() # className|varName
      self.writeAdv() # '.'
      self.writeAdv() # subroutineName
      self.writeAdv() # '('
      self.compileExpressionList()
      self.writeAdv() # ')'
      self.writeAdv() # ';'
    

    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</doStatement>\n')
    return

  def compileLet(self):
    self.outIndent()
    self.output1.write('<letStatement>\n')
    self.increaseIndent()

    self.writeAdv() # 'let'
    self.writeAdv() # varName
    #check if [] brackets are there or not 
    if str(self.currentToken) == '<symbol> [ </symbol>\n':
      self.writeAdv() # [
      self.compileExpression()
      self.writeAdv() # ]
    self.writeAdv() # '=' 
    self.compileExpression()
    self.writeAdv() # ';'


    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</letStatement>\n')
    return

  def compileWhile(self):
    self.outIndent()
    self.output1.write('<whileStatement>\n')
    self.increaseIndent()

    self.writeAdv() # 'while'
    self.writeAdv() # (
    self.compileExpression()
    self.writeAdv() # )
    self.writeAdv() # {
    self.compileStatements()
    self.writeAdv() # }


    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</whileStatement>\n')
    return

  def compileReturn(self):
    self.outIndent()
    self.output1.write('<returnStatement>\n')
    self.increaseIndent()

    self.writeAdv() # print return 
    # if expression compile that as well
    if self.checkMoreTerms():
      self.compileExpression()
    self.writeAdv() # ;

    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</returnStatement>\n')
    return

  def compileIf(self):
    self.outIndent()
    self.output1.write('<ifStatement>\n')
    self.increaseIndent()

    self.writeAdv() # 'if'
    self.writeAdv() # '('
    self.compileExpression()
    self.writeAdv() # ')'
    self.writeAdv() # '{'
    self.compileStatements()
    self.writeAdv() # '}'
    # check if else statment is there 
    if str(self.currentToken) == '<keyword> else </keyword>\n':
      self.writeAdv() # 'else'
      self.writeAdv() # '{'
      self.compileStatements()
      self.writeAdv() # '}'
    
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</ifStatement>\n')
    return

  def compileExpression(self):
    # begging of expression so add indent to parse tree
    self.outIndent()
    self.output1.write('<expression>\n')
    self.increaseIndent()

    # compile term calls itself recursively to take care of multiple terms ie. term (op term)*
    self.compileTerm()
    
    # expression is over, no more terms, decrease the indent
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</expression>\n')
    return

  def compileTerm(self):
    self.outIndent()
    self.output1.write('<term>\n')
    self.increaseIndent()

    # da first part of the token
    daToken = str(self.currentToken.split()[0])

    # check which type of term to compile
    if daToken == '<identifier>':
      lookAhead = self.tTp[self.tokenCounter+1]
      if lookAhead == '<symbol> [ </symbol>\n':
        self.writeAdv() # write the identifier varName
        self.writeAdv() # the [
        self.compileExpression()
        self.writeAdv() # the ]
      elif lookAhead == '<symbol> ( </symbol>\n':
        self.writeAdv() # subroutineName wrapped in identifier tags
        self.writeAdv() # '('
        self.compileExpressionList()
        self.writeAdv() # ')'
      elif lookAhead == '<symbol> . </symbol>\n':
        # subroutineName
        self.writeAdv() # className|varName
        self.writeAdv() # '.'
        self.writeAdv() # subroutineName
        self.writeAdv() # '('
        self.compileExpressionList()
        self.writeAdv() # ')'
      else:
        self.writeAdv() # just a varName
    elif daToken == '<integerConstant>':
      self.writeAdv()
    elif daToken == '<stringConstant>':
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> true </keyword>\n':
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> false </keyword>\n':
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> null </keyword>\n':
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> this </keyword>\n':
      self.writeAdv()
    elif str(self.currentToken) == '<symbol> ( </symbol>\n':
      self.writeAdv() # for (
      self.compileExpression()
      self.writeAdv() # for )
    elif str(self.currentToken) == '<symbol> - </symbol>\n':
      self.writeAdv()
      self.compileTerm()
    elif str(self.currentToken) == '<symbol> ~ </symbol>\n':
      self.writeAdv()
      self.compileTerm()
    
    
    # end of term decrease indent
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</term>\n')

    # check for op and then use recursion
    if self.checkOp():
      self.writeAdv() # write the op term
      self.compileTerm()

    #check if another term using recursion
    #if self.checkMoreTerms():
      #self.compileTerm()

    return

  def compileExpressionList(self):
    self.outIndent()
    self.output1.write('<expressionList>\n')
    self.increaseIndent()

    
    # check if 
    while self.checkMoreTerms():
      # actually compile an expression if not empty
      #print(self.currentToken)
      self.compileExpression()
      if str(self.currentToken) == '<symbol> , </symbol>\n':
        self.writeAdv() # ','

    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</expressionList>\n')
    return

  def outIndent(self):
    for i in range(self.indent):
      # change be careful below was old
      #self.output1.write('\t')
      self.output1.write('  ')
    return

  def advance(self):
    self.tokenCounter += 1
    self.currentToken = self.tTp[self.tokenCounter]

  def writeAdv(self):
    self.outIndent()
    self.output1.write(self.currentToken)
    self.advance()
    return

  def increaseIndent(self):
    self.indent += 1
    return

  def decreaseIndent(self):
    self.indent -= 1
    return

  def checkStatement(self):
    if str(self.currentToken) == '<keyword> if </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> let </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> while </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> do </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> return </keyword>\n':
      return True
    else:
      return False

  def checkOp(self):
    if str(self.currentToken) == '<symbol> + </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> - </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> * </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> / </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> &amp; </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> | </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> &lt; </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> &gt; </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> = </symbol>\n':
      return True
    else:
      return False

  def checkMoreTerms(self):

    daToken = str(self.currentToken.split()[0])

    if daToken == '<identifier>':
      lookAhead = self.tTp[self.tokenCounter+1]
      if lookAhead == '<symbol> [ </symbol>\n':
        return True
      elif lookAhead == '<symbol> ( </symbol>\n':
        return True
      elif lookAhead == '<symbol> . </symbol>\n':
        return True
      else:
        return True
    elif daToken == '<integerConstant>':
      return True
    elif daToken == '<stringConstant>':
      return True
    elif str(self.currentToken) == '<keyword> true </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> false </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> null </keyword>\n':
      return True
    elif str(self.currentToken) == '<keyword> this </keyword>\n':
      return True
    elif str(self.currentToken) == '<symbol> ( </symbol>\n':
      return True
      #check unary Op
    elif str(self.currentToken) == '<symbol> - </symbol>\n':
      return True
    elif str(self.currentToken) == '<symbol> ~ </symbol>\n':
      return True
    else:
      return False
    
