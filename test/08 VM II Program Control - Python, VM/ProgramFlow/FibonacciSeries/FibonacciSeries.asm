@1
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
A=M-1
D=M
@R15
M=D
@1
D=A
@THIS
D=A+D
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
@THAT
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
@1
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
@1
D=A
@THAT
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
@2
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
(main$MAIN_LOOP_START)
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
@main$COMPUTE_ELEMENT
D;JNE
@main$END_PROGRAM
0;JMP
(main$COMPUTE_ELEMENT)
@0
D=A
@THAT
A=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@THAT
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
@2
D=A
@THAT
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
@1
D=A
@THIS
A=A+D
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
D=D+M
@SP
A=M-1
M=D
@SP
A=M-1
D=M
@R15
M=D
@1
D=A
@THIS
D=A+D
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
@main$MAIN_LOOP_START
0;JMP
(main$END_PROGRAM)
