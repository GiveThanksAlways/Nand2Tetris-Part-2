def commandType(cmd1):
  if "push" in cmd1:
    return "C_PUSH"
  elif "pop" in cmd1:
    return "C_POP"
  elif "add" or "sub" or 'neg' or 'eq' or 'gt' or 'lt' or 'and' or 'or' or 'not' in cmd1:
    return "C_ARITHMETIC"
  elif 'label' in cmd1:
    return 'C_LABEL'
  elif 'goto' in cmd1:
    return 'C_GOTO'
  elif 'if' in cmd1:
    return 'C_IF'
  elif 'function' in cmd1:
    return 'C_FUNCTION'
  elif 'call' in cmd1:
    return 'C_CALL'
  elif 'return' in cmd1:
    return 'C_RETURN'
  
def getarg1(cmdarg1):
  
  arg1r = cmdarg1.split(' ')
  if len(arg1r) > 1:
    return arg1r[1]
  
def getarg2(cmdarg2):
  
  arg2r = cmdarg2.split(' ')
  if len(arg2r) > 2:
    
    return int(arg2r[2])
  
    # open the file and remove white space and comments
   
def printarray(array1):
  for i in array1:
    output.write(i)
    output.write('\n')
  return
   
def pushASM():
  pushASMarray= ["@SP",'A=M','M=D','@SP','M=M+1']
  printarray(pushASMarray)
  
  return

def addASM():
  addASMarray= ["@SP",'M=M-1','A=M-1','D=M','@SP','A=M','D=D+M','@SP','A=M-1','M=D']
  printarray(addASMarray)
  
  return

def subASM():
  subASMarray= ["@SP",'M=M-1','A=M-1','D=M','@SP','A=M','D=D-M','@SP','A=M-1','M=D']
  printarray(subASMarray)
  
  return

def negASM():
  negASMarray= ["@SP",'A=M-1','D=-M','@SP','A=M-1','M=D']
  printarray(negASMarray)
  
  return

def eqASM(i):
  eqASMarray= [
  "@SP",
  'M=M-1',
  "@SP",
  'A=M-1',
  'D=M',
  '@SP',
  'A=M',
  'D=D-M',
  '@TRUE'+str(i),
  'D;JEQ',
  '@SP',
  'A=M-1',
  'M=0',
  '@END'+str(i),
  '0;JMP',
  '(TRUE'+str(i)+')',
  '@SP',
  'A=M-1',
  'M=-1',
  '(END'+str(i)+')'
  ]
  printarray(eqASMarray)
  
  return

def gtASM(i):
  gtASMarray= [
  "@SP",
  'M=M-1',
  "@SP",
  'A=M-1',
  'D=M',
  '@SP',
  'A=M',
  'D=D-M',
  '@TRUE'+str(i),
  'D;JGT',
  '@SP',
  'A=M-1',
  'M=0',
  '@END'+str(i),
  '0;JMP',
  '(TRUE'+str(i)+')',
  '@SP',
  'A=M-1',
  'M=-1',
  '(END'+str(i)+')'
  ]
  printarray(gtASMarray)
  
  return
  
def ltASM(i):
  ltASMarray= [
  "@SP",
  'M=M-1',
  "@SP",
  'A=M-1',
  'D=M',
  '@SP',
  'A=M',
  'D=D-M',
  '@TRUE'+str(i),
  'D;JLT',
  '@SP',
  'A=M-1',
  'M=0',
  '@END'+str(i),
  '0;JMP',
  '(TRUE'+str(i)+')',
  '@SP',
  'A=M-1',
  'M=-1',
  '(END'+str(i)+')'
  ]
  printarray(ltASMarray)
  
  return
  
def andASM():
  andASMarray= [
  "@SP",
  'M=M-1',
  "@SP",
  'A=M-1',
  'D=M',
  '@SP',
  'A=M',
  'D=D&M',
  '@SP',
  'A=M-1',
  'M=D'
  ]
  printarray(andASMarray)
  
  return

def orASM():
  orASMarray= [
  "@SP",
  'M=M-1',
  "@SP",
  'A=M-1',
  'D=M',
  '@SP',
  'A=M',
  'D=D|M',
  '@SP',
  'A=M-1',
  'M=D'
  ]
  printarray(orASMarray)
  
  return
  
def notASM():
  notASMarray= [
  "@SP",
  'A=M-1',
  'D=M',
  'D=!D',
  '@SP',
  'A=M-1',
  'M=D'
  ]
  printarray(notASMarray)
  
  return
# get the item to push to stack
def pushitem(s,name):
  arg1 = getarg1(s)
  arg2 = getarg2(s)
  if arg1 == 'constant':
    output.write('@'+str(arg2))
    output.write('\nD=A\n') 
  elif arg1 == 'argument':
    argumentarray = [
      '@'+str(arg2),
      'D=A',
      '@ARG',
      'A=M+D',
      'D=M'
      ]
    printarray(argumentarray)
  elif arg1 == 'local':
    localarray = [
      '@'+str(arg2),
      'D=A',
      '@LCL',
      'A=M+D',
      'D=M'
      ]
    printarray(localarray)
  elif arg1 == 'this':
    thisarray = [
      '@'+str(arg2),
      'D=A',
      '@THIS',
      'A=M+D',
      'D=M'
      ]
    printarray(thisarray)
  elif arg1 == 'that':
    thatarray = [
      '@'+str(arg2),
      'D=A',
      '@THAT',
      'A=M+D',
      'D=M'
      ]
    printarray(thatarray)
  elif arg1 == 'static':
    staticarray = [
      '@'+name+'.'+str(arg2),
      'D=A' 
      ]
    printarray(staticarray)
  elif arg1 == 'pointer':
    pointerarray = [
      '@'+str(arg2),
      'D=A',
      '@THIS',
      'A=A+D',
      'D=A'
      ]
    printarray(pointerarray)
  elif arg1 == 'temp':
    temparray = [
      '@'+str(arg2),
      'D=A',
      '@5',
      'A=A+D',
      'D=A'
      ]
    printarray(temparray)
  
  
  return

def popASM(s,name):
  
  arg1 = getarg1(s)
  arg2 = getarg2(s)
  
  if arg1 != 'static':
    popASMarray= ["@SP",'A=M','D=M','@R15','M=D','@'+str(arg2),
      'D=A']
    printarray(popASMarray)
  
  if arg1 == 'constant':
    output.write('@'+str(arg2))
    output.write('\nM=D\n') 
  elif arg1 == 'argument':
    argumentarray = ['@ARG']
    printarray(argumentarray)
  elif arg1 == 'local':
    localarray = ['@LCL']
    printarray(localarray)
  elif arg1 == 'this':
    thisarray = ['@THIS']
    printarray(thisarray)
  elif arg1 == 'that':
    thatarray = ['@THAT']
    printarray(thatarray)
  elif arg1 == 'static':
    staticarray = ["@SP",'A=M','D=M','@R15','M=D',
      '@'+name+'.'+str(arg2),'D=A' 
      ]
    printarray(staticarray)
  elif arg1 == 'pointer':
    pointerarray = [
      '@THIS',
      'D=A+D'
      ]
    printarray(pointerarray)
  elif arg1 == 'temp':
    temparray = [
      '@5',
      'D=A+D'
      ]
    printarray(temparray)
  
  popASMarrayend= [
      'D=M+D',
      '@R14',
      'M=D',
      '@R15',
      'D=M',
      '@R14',
      'A=M',
      'M=D']
      
  
  if arg1 == 'pointer' or arg1 =='temp':
    
    printarray(['@R14','M=D','@R15','D=M','@R14','A=M','M=D'])
  else:
    printarray(popASMarrayend)
  return


import glob

for filename in glob.glob('*.vm'):
  
  content = []
  #print(filename)
  with open(filename) as f:
      for line in f:
          line = line.split('//', 1)[0]
          line = line.rstrip()
          content.append(line)
      
  content = [x.strip() for x in content]
  content[:] = [item for item in content if item != '']
  
  output = open(filename[:filename.index('.')]+'.asm','w')
  
  
  #1st pass
  n=0
  for command in content:
    
    #print(commandType(command))
    #print(command)
    
    #print(arg1find(command))
    #print(arg2find(command))
    
    # push assembly
    if commandType(command) == 'C_PUSH':
      # get arg to push onto stack
      
      pushitem(command,filename[:filename.index('.')])
        
      pushASM()
    
    elif commandType(command) == 'C_ARITHMETIC':
      if 'add' in command:
        addASM()
      elif 'sub' in command:
        subASM()
      elif 'neg' in command:
        negASM()
      elif 'eq' in command:
        eqASM(n)
        n+=1
      elif 'gt' in command:
        gtASM(n)
        n+=1
      elif 'lt' in command:
        ltASM(n)
        n+=1
      elif 'and' in command:
        andASM()
      elif 'or' in command:
        orASM()
      elif 'not' in command:
        notASM()
    elif commandType(command) == 'C_POP':
      popASM(command,filename[:filename.index('.')])
  
  
  #print(filename[:filename.index('.')])
  output.close()
  
  
      
