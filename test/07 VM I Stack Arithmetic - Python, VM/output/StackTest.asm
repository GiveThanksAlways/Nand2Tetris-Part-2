@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE0
D;JEQ
@SP
A=M-1
M=0
@END0
0;JMP
(TRUE0)
@SP
A=M-1
M=-1
(END0)
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE1
D;JEQ
@SP
A=M-1
M=0
@END1
0;JMP
(TRUE1)
@SP
A=M-1
M=-1
(END1)
@16
D=A
@SP
A=M
M=D
@SP
M=M+1
@17
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE2
D;JEQ
@SP
A=M-1
M=0
@END2
0;JMP
(TRUE2)
@SP
A=M-1
M=-1
(END2)
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE3
D;JLT
@SP
A=M-1
M=0
@END3
0;JMP
(TRUE3)
@SP
A=M-1
M=-1
(END3)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@892
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE4
D;JLT
@SP
A=M-1
M=0
@END4
0;JMP
(TRUE4)
@SP
A=M-1
M=-1
(END4)
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@891
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE5
D;JLT
@SP
A=M-1
M=0
@END5
0;JMP
(TRUE5)
@SP
A=M-1
M=-1
(END5)
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE6
D;JGT
@SP
A=M-1
M=0
@END6
0;JMP
(TRUE6)
@SP
A=M-1
M=-1
(END6)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32767
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE7
D;JGT
@SP
A=M-1
M=0
@END7
0;JMP
(TRUE7)
@SP
A=M-1
M=-1
(END7)
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@32766
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D-M
@TRUE8
D;JGT
@SP
A=M-1
M=0
@END8
0;JMP
(TRUE8)
@SP
A=M-1
M=-1
(END8)
@57
D=A
@SP
A=M
M=D
@SP
M=M+1
@31
D=A
@SP
A=M
M=D
@SP
M=M+1
@53
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M-1
D=M
@SP
A=M
D=D+M
@SP
A=M-1
M=D
@112
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M-1
D=M
@SP
A=M
D=D-M
@SP
A=M-1
M=D
@SP
A=M-1
D=-M
@SP
A=M-1
M=D
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D&M
@SP
A=M-1
M=D
@82
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M-1
D=M
@SP
A=M
D=D|M
@SP
A=M-1
M=D
@SP
A=M-1
D=M
D=!D
@SP
A=M-1
M=D
