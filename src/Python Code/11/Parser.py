from SymbolTable import SymbolTable,Node,LinkedList

from VMWriter import VMWriter

class Parser:
  def __init__(self, parserInput, parserOutput,daSymbolTable):
    
    self.tTp = [] #tokens to parse array aka tTp
    self.tTpcopy = [] #copy to help remove stuff
    self.tokenCounter = 0
    self.indent = 0

    # open the input.xml file made by the tokenizer (full of tokens ready to parse)
    with open(parserInput) as f:
      for line in f:
        self.tTpcopy.append(line)
    self.tTp = self.tTpcopy[1:-1] # remove unwanted stuff from copy

    self.output1 = open(parserOutput+'.xml', 'w') 
    #output to write to
    self.theVMWriter = VMWriter(parserOutput)

    
    self.currentTokenArr = self.tTp[self.tokenCounter].split(' ')
    self.currentToken = self.tTp[self.tokenCounter] # first token
    self.className = ''
    self.subroutineVoid = False
    self.iflabel = 0
    self.whilelabel = 0
    self.constructor = False
    self.functionType = ''
    self.subroutineName = ''
    self.array = False

    # get symbol table and everything started
    self.theSymbolTable = daSymbolTable
    self.theSymbolTable.classStart()
    self.compileClass() # start compiling


    self.output1.close() # close the file when done
    
# compile the class
  def compileClass(self):
    self.output1.write('<class>'+'\n')
    self.increaseIndent()
    self.writeAdv() # 'class'
    # save the class name for symbol table
    self.className = str(self.currentToken.split()[1]) 
    self.writeAdv() #  className
    self.writeAdv() # '{'


    self.compileClassVarDec()
  


    self.compileSubroutine()
    self.outIndent()
    self.output1.write(self.currentToken)
    self.output1.write('</class>'+'\n')

    # recursion to compile multiple classes in one file
    #print(self.tokenCounter)
    #print(len(self.tTp))
    daSize = len(self.tTp)
    if self.tokenCounter+1 != daSize:
      #print('hello')
      lookAhead = str(self.tTp[self.tokenCounter+1]).split()[1]
      #print(lookAhead)
      if lookAhead == 'class':
        #self.tokenCounter+= 2
        self.writeAdv()
        #print(self.currentToken)
        self.compileClass() # start compiling again using recursion!!!!!


    #self.theSymbolTable.viewTableCST()
    return 

  def compileClassVarDec(self):
    

    if str(self.currentToken) == '<keyword> field </keyword>\n' or str(self.currentToken) == '<keyword> static </keyword>\n':
      self.outIndent()
      self.output1.write('<classVarDec>\n')
      self.increaseIndent()
      # while loop takes care of (varName)*
      classVarkind = self.currentToken.split()[1]
      classVartype = self.tTp[self.tokenCounter+1].split()[1]
      everytwo = 0
      start = 1
      while str(self.currentToken) != '<symbol> ; </symbol>\n':

        if everytwo % 2 == 0 and start > 2:
          daname = self.currentToken.split()[1]
          self.theSymbolTable.define(daname,classVartype,classVarkind)
          
        self.writeAdv() 
        start += 1
        everytwo += 1
        
        
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
    
    
    self.functionType = str(self.currentToken.split()[1]) # save if it is constructor,function, or method
    if str(self.currentToken.split()[1]) == 'constructor':
      self.constructor = True
    else:
      self.constructor = False

    self.writeAdv() # constructor|function|method
    if str(self.currentToken.split()[1]) == 'void':
      self.subroutineVoid = True
    else:
      self.subroutineVoid = False

    self.writeAdv() # void|type
    self.subroutineName = str(self.currentToken.split()[1]) 
    self.writeAdv() # subroutineName
    self.writeAdv() # '('
    
    self.theSymbolTable.startSubroutine()
    if self.functionType == 'method':
      daname = 'this'
      datype = self.className
      dakind = 'argument'
      self.theSymbolTable.defineMethod(daname,datype,dakind)

    self.compileParameterList()
    
    self.writeAdv() # ')' for end of parameterlist

    self.outIndent()
    self.output1.write('<subroutineBody>\n')
    self.increaseIndent()
    self.writeAdv() # print the {

    # compile all of the varDecs first
    if str(self.currentToken) == '<keyword> var </keyword>\n':
      self.compileVarDec()
    
    # VM code write function down
    the999 = self.theSymbolTable.varCount('var')
    #print(subroutineName)
    self.theVMWriter.writeFunction(self.className,self.subroutineName,the999)
    
    # code to set the 'this' to point to passed object
    if self.constructor == True:
      self.theVMWriter.writePush('constant',self.theSymbolTable.varCount('field'))
      self.theVMWriter.writeCall('Memory.alloc',1)
      self.theVMWriter.writePop('pointer',0)
    elif self.functionType == 'method':
      self.theVMWriter.writePush('argument',0)
      self.theVMWriter.writePop('pointer',0)
      #daname = 'this'
      #datype = self.className
      #dakind = 'argument'
      #self.theSymbolTable.defineMethod(daname,datype,dakind)
    # enter statements and statements calls itself recursively
    self.compileStatements()  
     
    self.writeAdv() # } ending the subroutineBody
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</subroutineBody>\n')
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</subroutineDec>\n')
    #self.theSymbolTable.viewTableMST()
    
    # keep track of methods in symbol table
    
    self.theSymbolTable.defineSubroutineTracker(self.subroutineName,'method' ,self.className,self.subroutineVoid)
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
    everythree = 0
    while str(self.currentToken) != '<symbol> ) </symbol>\n':
      if everythree % 3 == 0:
        daname = self.tTp[self.tokenCounter+1].split()[1]
        datype = self.tTp[self.tokenCounter].split()[1]
        dakind = 'argument'
        self.theSymbolTable.defineMethod(daname,datype,dakind)

      self.writeAdv()
      everythree += 1
      
    
    
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</parameterList>\n')
    return

  def compileVarDec(self):
    
    self.outIndent()
    self.output1.write('<varDec>\n')
    self.increaseIndent()

    
    self.writeAdv() # 'var'
    everytwo = 0
    datype = self.tTp[self.tokenCounter].split()[1]
    self.writeAdv() #  type
    while str(self.currentToken) != '<symbol> ; </symbol>\n':
      if everytwo % 2 == 0:
        daname = self.tTp[self.tokenCounter].split()[1]
        dakind = 'var'
        self.theSymbolTable.defineMethod(daname,datype,dakind)

      self.writeAdv()
      everytwo += 1
      
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
        if self.constructor == True:
          2+2
          #self.theVMWriter.writePush('pointer',0)
        self.compileReturn()

    
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</statements>\n')
    return

  def compileDo(self):
    self.outIndent()
    self.output1.write('<doStatement>\n')
    self.increaseIndent()
    DoSubroutineName = ''
    self.writeAdv() # 'do'
    # subroutineCall which is a term, inside of an expression
    
    # LL(2) grammar part. 
    # look ahead one token to see if ( or . for two types of subroutine calls
    lookAhead = self.tTp[self.tokenCounter+1]
    if lookAhead == '<symbol> ( </symbol>\n':
      callF = str(self.currentToken.split()[1])
      DoSubroutineName = callF
      #print(callF)
      self.theVMWriter.writePush('pointer','0')
      self.writeAdv() # subroutineName wrapped in identifier tags
      self.writeAdv() # '('
      self.compileExpressionList()
      self.writeAdv() # ')'
      self.writeAdv() # ';'
      #checkClass = self.theSymbolTable.getKind(callF)
      # check if the calling class is the same as the current class. If not, we need to find the write method/function/subroutine from that calling class
      #if(checkClass != self.className):
        #numOfarg = self.theSymbolTable.getIDofClass(callF,checkClass)
      #else:
      #numOfarg = self.theSymbolTable.getID(callF)
      numOfarg = self.theSymbolTable.getIDofClass(callF,self.className)
      
      self.theVMWriter.writeCall(self.className+'.'+callF,str(numOfarg)) # this is the call that will print for methods ie erase() and only for Do statements where it is just a method of the current class being compiled  
      if self.theSymbolTable.getVoid(callF,self.className):
        self.theVMWriter.writePop('temp','0')
    else:
      # subroutineName
      otherClassname = str(self.currentToken.split()[1])
      self.writeAdv() # className|varName
      self.writeAdv() # '.'
      callF = str(self.currentToken.split()[1]) # subroutineName
      if self.theSymbolTable.getKind(otherClassname) != None:
        theSegment = self.theSymbolTable.getKind(otherClassname)
        theIndex = self.theSymbolTable.getID(otherClassname)
        self.theVMWriter.writePush(theSegment,theIndex)
      self.writeAdv() # subroutineName
      self.writeAdv() # '('
      self.compileExpressionList()
      self.writeAdv() # ')'
      self.writeAdv() # ';'
      #checkClass = self.theSymbolTable.getKind(callF)
      
        #numOfarg = self.theSymbolTable.getIDofClass(callF,self.className)
        #realClassName = self.theSymbolTable.getType(otherClassname)
      #print(otherClassname)
      # this will check all kinds ie Class Names. If None, then we have an acutal class 
      if self.theSymbolTable.getKind(otherClassname) == None: 
        numOfarg = self.theSymbolTable.getIDofClass(callF,otherClassname)
        self.theVMWriter.writeCall(otherClassname+'.'+callF,str(numOfarg)) # This writeCall is for other classes ie Screen.drawRectangle
        if self.theSymbolTable.getVoid(callF,otherClassname):
          self.theVMWriter.writePop('temp','0')
      # this is the loop for the object 
      else:
        #theSegment = self.theSymbolTable.getKind(otherClassname)
        #theIndex = self.theSymbolTable.getID(otherClassname)
        #self.theVMWriter.writePush(theSegment,theIndex)
        # find the realClassName or the class name of the object 
        realClassName = self.theSymbolTable.getType(otherClassname)
        if realClassName != None:
            #print('hello\n\n\n\n')
            #print(otherClassname)
            #print(realClassName)
            numOfarg = self.theSymbolTable.getIDofClass(callF,realClassName)
            self.theVMWriter.writeCall(realClassName+'.'+callF,str(numOfarg)) # write call for objects ie square.moveRight, it is the object, not the class ie game.run(), game is of the SquareGame class, run is the method game is the object 
            if self.theSymbolTable.getVoid(callF,realClassName):
              self.theVMWriter.writePop('temp','0')
            #print("current class " + self.className)
            #print("realClassname " + str(realClassName))
            #print("otherClassname " + otherClassname)
            #print("callF --> " + callF)
            #print("numOfarg ---> " + str(numOfarg))
        else:
          numOfarg = self.theSymbolTable.getIDofClass(callF,otherClassname)
          self.theVMWriter.writeCall(otherClassname+'.'+callF,str(numOfarg))
          if self.theSymbolTable.getVoid(callF,otherClassname):
            self.theVMWriter.writePop('temp','0')


    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</doStatement>\n')
    #if self.theSymbolTable.getVoid(DoSubroutineName):
      #print(DoSubroutineName)
      # if the method call was void
      # self.theSymbolTable.getVoid(callF)
      #print(DoSubroutineName)
      #self.theVMWriter.writePop('temp','0')

    return

  def compileLet(self):
    self.outIndent()
    self.output1.write('<letStatement>\n')
    self.increaseIndent()

    self.writeAdv() # 'let'
    letVarname = str(self.currentToken.split()[1]) 
    self.writeAdv() # varName
    #check if [] brackets are there or not 
    if str(self.currentToken) == '<symbol> [ </symbol>\n':
      self.array = True
      # push a from a[i]
      theSegment = self.theSymbolTable.getKind(letVarname)
      theIndex = self.theSymbolTable.getID(letVarname)
      self.theVMWriter.writePush(theSegment,theIndex)
      self.writeAdv() # [
      self.compileExpression()
      self.writeAdv() # ]
      # add
      self.theVMWriter.writeArithmetic('+')
      
    self.writeAdv() # '=' 
    self.compileExpression() # 19 expression in example
    self.writeAdv() # ';'
   
    if self.array:
      #self.theVMWriter.writePop('pointer','1')
      self.theVMWriter.writePop('temp',0)
      self.theVMWriter.writePop('pointer',1)
      self.theVMWriter.writePush('temp',0)
      self.theVMWriter.writePop('that',0)
      self.array = False
    else:
      # now VM code for pop stack result to varName spot
      
      theSegment = self.theSymbolTable.getKind(letVarname)
      theIndex = self.theSymbolTable.getID(letVarname)
      self.theVMWriter.writePop(theSegment,theIndex)

    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</letStatement>\n')
    return

  def compileWhile(self):
    self.outIndent()
    self.output1.write('<whileStatement>\n')
    self.increaseIndent()

    whileLabel1 = str('whileL'+str(self.whilelabel))
    self.whilelabel += 1
    whileLabel2 = str('whileL'+str(self.whilelabel))
    self.whilelabel += 1
    self.theVMWriter.writeLabel(whileLabel1) # label L1

    self.writeAdv() # 'while'
    self.writeAdv() # (
    self.compileExpression()
    
    # taken care of by expression-compileTerm
    self.theVMWriter.writeArithmetic('NOT') # push !(cond)
    self.theVMWriter.writeIf(whileLabel2)

    self.writeAdv() # )
    self.writeAdv() # {
    self.compileStatements() # VM code for {}
    self.writeAdv() # }
    self.theVMWriter.writeGoto(whileLabel1) # go to L1
    self.theVMWriter.writeLabel(whileLabel2) # label 2
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

    # if void push 0 ,if not return top of stack
    if self.subroutineVoid:
      self.theVMWriter.writePush('constant',0)
    # VM code return
    self.theVMWriter.writeReturn()
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

    self.theVMWriter.writeArithmetic('NOT') # push !(cond)
    ifLabel1 = str('ifL'+str(self.iflabel))
    self.iflabel += 1
    self.theVMWriter.writeIf(ifLabel1)

    self.writeAdv() # '{'
    self.compileStatements()

    ifLabel2 = str('ifL'+str(self.iflabel))
    self.iflabel += 1
    self.theVMWriter.writeGoto(ifLabel2)

    self.theVMWriter.writeLabel(ifLabel1)
    self.writeAdv() # '}'
    # check if else statment is there 
    if str(self.currentToken) == '<keyword> else </keyword>\n':
      self.writeAdv() # 'else'
      self.writeAdv() # '{'
      self.compileStatements()
      self.writeAdv() # '}'
    
    self.theVMWriter.writeLabel(ifLabel2)
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</ifStatement>\n')
    return

  def compileExpression(self):
    # begging of expression so add indent to parse tree
    self.outIndent()
    self.output1.write('<expression>\n')
    self.increaseIndent()

    # VM codeWrite(exp) algorithm
    #self.codeWrite()

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
    VMToken = str(self.currentToken.split()[1])
    
    # check which type of term to compile
    if daToken == '<identifier>':
      lookAhead = self.tTp[self.tokenCounter+1]
      if lookAhead == '<symbol> [ </symbol>\n': # then it is an array
        #print('array')
        theSegment = self.theSymbolTable.getKind(VMToken)
        theIndex = self.theSymbolTable.getID(VMToken)
        self.theVMWriter.writePush(theSegment,theIndex)
        #arrayNumber = self.tTp[self.tokenCounter+2].split()[1]
        #arrayName = VMToken
        self.writeAdv() # write the identifier varName
        self.writeAdv() # the [
        self.compileExpression()
        self.writeAdv() # the ]
        #theSegment = self.theSymbolTable.getKind(arrayName)
        #theIndex = self.theSymbolTable.getID(arrayName)
        #self.theVMWriter.writePush(theSegment,theIndex)
        # add i + base of array
        self.theVMWriter.writeArithmetic('+')
        self.theVMWriter.writePop('pointer','1')
        self.theVMWriter.writePush('that','0')
        #self.writeAdv() # '='
        #self.compileExpression()

        #self.theVMWriter.writePop('temp',0)
        #self.theVMWriter.writePop('pointer',1)
        #self.theVMWriter.writePush('temp',0)
        #self.theVMWriter.writePop('that',0)
        
      elif lookAhead == '<symbol> ( </symbol>\n': # then it is a subroutine call
      # VM use That point
        #call f
        callF = str(self.currentToken.split()[1])
        self.theVMWriter.writePush('argument','0')
        self.writeAdv() # subroutineName
        self.writeAdv() # '('
        self.compileExpressionList()
        self.writeAdv() # ')'
        #numOfarg = self.theSymbolTable.getID(callF)
        numOfarg = self.theSymbolTable.getIDofClass(callF,self.className)
        self.theVMWriter.writeCall(self.className+'.'+callF,str(numOfarg)) # never got hit for SquareGame
        if self.theSymbolTable.getVoid(callF,self.className):
          self.theVMWriter.writePop('temp','0')
      elif lookAhead == '<symbol> . </symbol>\n': # call to another class
        # subroutineName
        # VM use THIS pointer
        otherClassname = str(self.currentToken.split()[1])
        self.writeAdv() # className|varName
        self.writeAdv() # '.'
        callF = str(self.currentToken.split()[1]) # subroutineName
        self.writeAdv() # subroutineName
        self.writeAdv() # '('
        self.compileExpressionList()
        self.writeAdv() # ')'
        #numOfarg = self.theSymbolTable.getID(callF)
        
        # maybe other type of class check

        realClassName = self.theSymbolTable.getType(otherClassname)

        #print("otherClassname " + otherClassname)
        #print("realClassName " + str(realClassName))
        if self.theSymbolTable.getID(otherClassname) != None:
          self.theVMWriter.writePush(self.theSymbolTable.getKind(otherClassname),self.theSymbolTable.getID(otherClassname))
        # if it is not None then we have a object 
        if realClassName != None:
          numOfarg = self.theSymbolTable.getIDofClass(callF,realClassName)
          self.theVMWriter.writeCall(realClassName+'.'+callF,str(numOfarg)) # never got hit for SquareGame
          if self.theSymbolTable.getVoid(callF,realClassName):
            self.theVMWriter.writePop('temp','0')
        else:
          # only new from constructor in SquareGame.jack and keyPressed from Keyboard.keyPressed() call which is odd.
          numOfarg = self.theSymbolTable.getIDofClass(callF,otherClassname)
          self.theVMWriter.writeCall(otherClassname+'.'+callF,str(numOfarg)) 
          if self.theSymbolTable.getVoid(callF,otherClassname):
            self.theVMWriter.writePop('temp','0')

        #f self.theSymbolTable.getVoid(callF):
          #self.theVMWriter.writePop('temp','0')
        #if callF == 'new': # already handled by let statement
          #2+2
          # if new pop the x address let x = stuff
          #theNewAddress = str(self.tTp[almostNew-2].split()[1])
          #theSegment = self.theSymbolTable.getKind(theNewAddress)
          #theIndex = self.theSymbolTable.getID(theNewAddress)
          #self.theVMWriter.writePop(theSegment,theIndex)
      else: # varName
        theSegment = self.theSymbolTable.getKind(VMToken)
        theIndex = self.theSymbolTable.getID(VMToken)
        self.theVMWriter.writePush(theSegment,theIndex)
        self.writeAdv() # just a varName
    elif daToken == '<integerConstant>':
      self.theVMWriter.writePush('constant',VMToken)
      self.writeAdv()
    elif daToken == '<stringConstant>':
      #if self.tTp[self.tokenCounter-1].split()[1] == '=':
      arrayVMToken = self.currentToken.split()
      #print(str(''.join(arrayVMToken[1:-1])))
      eachletter = list(' '.join(arrayVMToken[1:-1]))
      #print(eachletter)
      self.theVMWriter.writePush('constant',len(eachletter))
      self.theVMWriter.writeCall('String.new',1)
      for i in range(len(eachletter)):
        self.theVMWriter.writePush('constant',ord(eachletter[i]))
        self.theVMWriter.writeCall('String.appendChar',2)
        
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> true </keyword>\n':
      self.theVMWriter.writePush('constant',1)
      self.theVMWriter.writeArithmetic('NEG')
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> false </keyword>\n':
      self.theVMWriter.writePush('constant',0)
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> null </keyword>\n':
      self.theVMWriter.writePush('constant',0)
      self.writeAdv()
    elif str(self.currentToken) == '<keyword> this </keyword>\n':
      self.theVMWriter.writePush('pointer',0)
      self.writeAdv()
    elif str(self.currentToken) == '<symbol> ( </symbol>\n':
      self.writeAdv() # for (
      self.compileExpression()
      self.writeAdv() # for )
    elif str(self.currentToken) == '<symbol> - </symbol>\n':
      # negative number
      self.writeAdv()
      self.compileTerm()
      self.theVMWriter.writeArithmetic('NEG') # now write op
    elif str(self.currentToken) == '<symbol> ~ </symbol>\n':
      self.writeAdv()
      self.compileTerm()
      self.theVMWriter.writeArithmetic('~') # now write op
    
    
    # end of term decrease indent
    self.decreaseIndent()
    self.outIndent()
    self.output1.write('</term>\n')

    # check for op and then use recursion
    if self.checkOp():
      opTerm = str(self.currentToken.split()[1]) # save op to write after
      self.writeAdv() # write the op term
      self.compileTerm()
      self.theVMWriter.writeArithmetic(opTerm) # now write op
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
    elif str(self.currentToken) == '<symbol> ^ </symbol>\n':
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
    
