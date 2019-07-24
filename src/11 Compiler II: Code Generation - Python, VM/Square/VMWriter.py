class VMWriter:

  def __init__(self, VMWriterOutput):
    self.output = open(str(VMWriterOutput)+'.vm', 'w')

  def writePush(self,segment,index):
    if segment != None and index != None:
      self.output.write('push '+segment+' '+str(index)+'\n')
    return

  def writePop(self,segment,index):
    if segment != None and index != None:
      self.output.write('pop '+segment+' '+str(index)+'\n')
    return

  def writeArithmetic(self,command):
    somethingHappened = True
    if command == '+':
      self.output.write('add')
    elif command == '-':
      self.output.write('sub')
    elif command == 'NEG':
      self.output.write('neg')
    elif command == '=':
      self.output.write('eq')
    elif command == '&gt;':
      self.output.write('gt')
    elif command == '&lt;':
      self.output.write('lt')
    elif command == '&amp;':
      self.output.write('and')
    elif command == '|':
      self.output.write('or')
    elif command == 'NOT':
      self.output.write('not')
    elif command == '^':
      self.writeCall('Math.power',2)
      somethingHappened = False
    elif command == '*':
      self.writeCall('Math.multiply',2)
      somethingHappened = False
    elif command == '/':
      self.writeCall('Math.divide',2)
      somethingHappened = False
    elif command == '~':
      #print('encontered a  ~ symbol')  boolean negation
      self.output.write('not')
    else:
      somethingHappened = False

    if somethingHappened:
      self.output.write('\n')
      


    return

  def writeLabel(self,label):
    self.output.write('label '+label+'\n')
    return
  
  def writeGoto(self,label):
    self.output.write('goto '+label+'\n')
    return

  def writeIf(self,label):
    self.output.write('if-goto '+label+'\n') 
    return

  def writeCall(self,name,nArgs):
    if nArgs == 0:
      self.output.write('call '+name+'\n')
    else:
      self.output.write('call '+name+' '+str(nArgs)+'\n')

    return

  def writeFunction(self,ClassName,name,nLocals):
    self.output.write('function '+ClassName+'.'+name+' '+str(nLocals)+'\n')
    return

  def writeReturn(self):
    self.output.write('return'+'\n')
    return

