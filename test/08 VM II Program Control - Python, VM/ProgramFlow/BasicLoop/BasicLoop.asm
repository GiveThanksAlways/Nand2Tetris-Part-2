@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
A=M-1
D=M
@R15
M=D
@0
D=A
@LCL
D=M+D
@R14
M=D
@R15
D=M
@R14
A=M
M=D
@SP
M=M-1
(main$LOOP_START)
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@0
D=A
@LCL
A=M+D
D=M
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
@SP
A=M-1
D=M
@R15
M=D
@0
D=A
@LCL
D=M+D
@R14
M=D
@R15
D=M
@R14
A=M
M=D
@SP
M=M-1
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
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
D=M
@R15
M=D
@0
D=A
@ARG
D=M+D
@R14
M=D
@R15
D=M
@R14
A=M
M=D
@SP
M=M-1
@0
D=A
@ARG
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@main$LOOP_START
D;JNE
@0
D=A
@LCL
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
