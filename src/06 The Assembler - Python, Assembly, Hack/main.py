import code 
content = []

# dictionary with Jack built in labels for pointers
dict1 = {'R0':0,'R1':1,'R2':2,'R3':3,'R4':4,'R5':5,'R6':6,'R7':7,'R8':8,'R9':9,'R10':10,'R11':11,'R12':12,'R13':13,'R14':14,'R15':15,'SCREEN':16384,'KBD':24576,'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4}

# function to determine if value is an integer or not
def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

#with open('input.txt') as f:
#content = f.readlines()
    
with open("input.txt") as f:
    for line in f:
        line = line.split('//', 1)[0]
        line = line.rstrip()
        content.append(line)
    
content = [x.strip() for x in content]
content[:] = [item for item in content if item != '']


output = open('output.txt','w')

LOOPS = 0
n = 16
#1st pass
for command in content:
  if "(" in command:
    dict1[command[1:len(command)-1]]=LOOPS
    LOOPS-=1
  LOOPS+=1
  
  
  


#2nd pass
for command in content:
  
  if "@" in command : # if A command
    if not RepresentsInt(command[1:]):
      # if symbol not in dictionary, then add
      if dict1.get(command[1:]) == None:
        dict1[command[1:]]=n 
        n+=1
      
    string1 = str(command[1:])
    if not RepresentsInt(command[1:]): # symbol handling
      string1 = dict1.get(string1)
      #print("String1 "+str(string1))
      #print(command[1:])
    
      #print(string1)
      #print(' '.join(format(ord(x), 'b') for x in string1))
    number = int(string1)
      #print(number)
    get_bin = lambda x, n: format(x, 'b').zfill(n)
      #print(get_bin(number, 15))
    commandnumber = ''.join(('0',get_bin(number, 15)))
      #print(commandnumber)
    output.write(commandnumber)
    output.write('\n')
  elif "=" in command or ";" in command: # if C command
    ccom = str(command)
    cmd = ''
    jmp = ''
    dest= ''
    if ccom.find('=') != -1: # if = is there then dest
      dest = ccom[0:ccom.find('=')]
      cmd = ccom[ccom.find('=')+1:len(ccom)]
      
    if ccom.find(';') != -1: # if ; is there then jmp
      jmp = ccom[ccom.find(';')+1:len(ccom)]
      cmd = ccom[0:ccom.find(';')]
      
    if jmp == '':
      jmp = "000"
    else:
      spot = code.x.index(jmp)-1
      jmptemp = code.x[spot]
      jmp = jmptemp
    
    if dest == '':
      dest = "000"
    else:
      spot =max(loc for loc, val in enumerate(code.x) if val == dest)-1
      desttemp = code.x[spot]
      dest = desttemp
      
    spot = code.x.index(cmd)-1
    cmdtemp = code.x[spot]
    cmd = cmdtemp
        
    # now print c command
    output.write('111'+cmd+dest+jmp)
    output.write('\n')
    
    
output.close()

  
#print(dict1)

    
