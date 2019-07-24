class Node:
  def __init__(self,hashTable,addnext_node = None):
    # each node will consist of a hashTable and the pointer that points to the next hashTable
    self.hashTable = hashTable
    self.nextnode = addnext_node

  def setNext(self,addnext_node):
    self.nextnode = addnext_node
  
  def getNext(self):
    return self.nextnode

  def getHashTable(self):
    return self.hashTable

class LinkedList:
  def __init__(self):
    self.first_node = None
  
  def insert(self,hashTable):
    inserted_node = Node(hashTable)
    inserted_node.setNext(self.first_node)
    self.first_node = inserted_node

  def resetMethodTable(self):
    self.first_node = None

  def viewTable(self):
    start = self.first_node
    #print(start.getNext())
    # run through linked list of nodes to print each one
    while start != None:
      #print('hello')
      print(start.getHashTable())
      for keys in start.getHashTable():
        #print(keys)
        values = start.getHashTable()[keys]
        #print(values)
      # get the next node
      start = start.getNext()
  
  def transverse(self,key,identifier):
    start = self.first_node
    #print(start.getNext())
    # run through linked list of nodes to print each one
    while start != None:
      #look at the keys and their values
      #for keys in start.getHashTable():
        #print(keys)
        #values = start.getHashTable()[keys]
        
        #print(values)
      value = start.getHashTable()['name']
      if identifier == value:
        #print(start.getHashTable()[key])
        #print(identifier)
        if key in start.getHashTable():
          return start.getHashTable()[key]
      # get the next node
      start = start.getNext()
    return None

class SymbolTable:
  def __init__(self):
    self.classSymbolTable = LinkedList()
    self.methodSymbolTable = LinkedList()
    self.staticCount = 0
    self.fieldCount = 0
    self.argumentCount = 0
    self.totalvarCount = 0


  def startSubroutine(self):
    # clear the subroutine hashtable and reset argument count
    self.methodSymbolTable.resetMethodTable()
    self.argumentCount = 0
    self.totalvarCount = 0
    return

  def varCount(self,kind):
    if kind == 'var':
      return self.totalvarCount
    elif kind == 'argument':
      return (self.argumentCount-1)
    elif kind == 'field':
      return self.fieldCount
    elif kind == 'static':
      return self.staticCount

  def classStart(self):
    self.fieldCount = 0 
    self.staticCount = 0
    return

  def addID(self,name,theType,kind):
    
    if kind == 'var':
      self.totalvarCount += 1
      return (self.totalvarCount - 1)
    elif kind == 'argument':
      self.argumentCount += 1
      return (self.argumentCount - 1)
    elif kind == 'static':
      self.staticCount += 1
      return (self.staticCount - 1)
    elif kind == 'field':
      self.fieldCount += 1
      return (self.fieldCount - 1)
    elif theType == 'method':
      return (self.argumentCount)
    elif kind == 'OS':
      return str(theType)
    
    return

  def defineSubroutineTracker(self,name,theType,kind,voidinput):
    # keep track of subroutines for later use
    self.classSymbolTable.insert({'name' : name,'type': theType,'kind':kind,'#':self.addID(name,theType,kind),'void':voidinput}) 

    return

  def define(self,name,theType,kind):
    # each row is a hashTable or dictionary
    # add the row to the symbolTable 
    # insert hashtable (dictionary) into linked list
    self.classSymbolTable.insert({'name' : name,'type': theType,'kind':kind,'#':self.addID(name,theType,kind)}) 

    return

  def defineMethod(self,name,theType,kind):
    # each row is a hashTable or dictionary
    # add the row to the symbolTable 
    # insert hashtable (dictionary) into linked list
    self.methodSymbolTable.insert({'name' : name,'type': theType,'kind':kind,'#':self.addID(name,theType,kind)}) 

    return

  def viewTableCST(self):
    print('\n    ----------class  symbol table----------')
    self.classSymbolTable.viewTable()

  def viewTableMST(self):
    print('\n    ----------method symbol table----------')
    self.methodSymbolTable.viewTable()

  def lookAtEachRow(self):
    self.classSymbolTable.transverse('x')
    self.methodSymbolTable.transverse('x')
    return

  def getKind(self,identifier):
    itwashere = self.methodSymbolTable.transverse('kind',identifier)
    if itwashere != None:
      if itwashere == 'var':
        return 'local'
      elif itwashere == 'argument':
        return 'argument'
    else:
      staticOrField = self.classSymbolTable.transverse('kind',identifier)
      if staticOrField == 'static':
        return 'static'
      elif staticOrField == 'field':
        return 'this'
      
      return 
  
  def getID(self,identifier):
    itwashere = self.methodSymbolTable.transverse('#',identifier)
    if itwashere != None:
      return itwashere
    else:
      return self.classSymbolTable.transverse('#',identifier)
  
  def getVoid(self,identifier):
    itwashere = self.methodSymbolTable.transverse('void',identifier)
    if itwashere != None:
      return itwashere
    else:
      return self.classSymbolTable.transverse('void',identifier)

