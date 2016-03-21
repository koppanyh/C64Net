#!/usr/bin/env python
#Created by Koppany Horvath
#Date 2016-03-10
cmds = ["END","FOR","NEXT","DATA","INPUT#","INPUT","DIM","READ","LET","GOTO","RUN","IF","RESTORE","GOSUB","RETURN","REM","STOP","ON","WAIT","LOAD","SAVE","VERIFY","DEF","POKE","PRINT#","PRINT","CONT","LIST","CLR","CMD","SYS","OPEN","CLOSE","GET","NEW","TAB(","TO","FN","SPC(","THEN","NOT","STEP","+","-","*","/","^","AND","OR",">","=","<","SGN","INT","ABS","USR","FRE","POS","SQR","RND","LOG","EXP","COS","SIN","TAN","ATN","PEEK","LEN","STR$","VAL","ASC","CHR$","LEFT$","RIGHT$","MID$","GO"] #list of basic commands
#cmds 128 - 203

btemp = []
basic = []
inp = ""
ptr = 0
print "Blank Line To Finish"
while 1: #input basic code
	inp = raw_input("- ").upper().strip()
	if inp == "": break
	btemp.append(inp)
def natsor(g): #used for sorting
	return int(g.split(" ")[0])
btemp.sort(key=natsor) #sort basic program by line number

for inp in btemp:
	for y in inp: #out of bounds detection
		if ord(y) < 32 or ord(y) > 90:
			print "String contains illegal character: "+y
			exit()
	basic.append(0) #lsb next pointer
	basic.append(0) #msb next pointer
	num = int(inp[:inp.find(" ")])
	inp = inp[inp.find(" ")+1:]
	basic.append(num%256) #lsb line number
	basic.append(num/256) #msb line number
	inp2 = inp.split("\"") #split by quote
	for i in range(len(inp2)):
		if i%2: #string in quotes, no modification
			basic.append(34)
			for j in inp2[i]: basic.append(ord(j))
			basic.append(34)
		else: #commands and stuff
			for j in range(76): inp2[i] = inp2[i].replace(cmds[j],chr(j+128))
			for j in range(len(inp2[i])): basic.append(ord(inp2[i][j]))
	basic.append(0) #end of line
	basic[ptr] = (len(basic)+2049)%256
	basic[ptr+1] = (len(basic)+2049)/256
	ptr = len(basic)
for i in range(2): basic.append(0)
blen = len(basic)

#def pro(g):
#	if g>31 and g<91: return "\t"+chr(g)
#	elif g>127 and g<204: return "\t"+cmds[g-128]
#	else: return ""
#for i in range(blen): print i+2049,"\t",basic[i],pro(basic[i])

#--------------------------------------------------------------------------------------------#

fcont = "C64-TAPE-RAW\x01\x00\x00\x00"
ftemp = ""
fdata = ""

l = "\x56"
m = "\x42"
s = "\x30"

def binToPulse(g): #2 lm; 1 ms; 0 sm; - s; x ls
	if g == "1": return m+s
	elif g == "0": return s+m
	elif g == "2": return l+m
	elif g == "-": return s
	elif g == "x": return l+s

def toTapBin(g): #turns 0-255 number to LM xx xx xx xx xx xx xx xx nn format
	g = bin(g)[2:]
	g = "0000000"+g
	g = g[-1:-9:-1]
	if g.count("1")%2: g+="0"
	else: g+="1"
	g = "2"+g
	return "".join([binToPulse(y) for y in g])

for i in range(27136): ftemp += s #leader block
for i in range(9,0,-1): ftemp += toTapBin(128+i) #header1 sync
fdata += toTapBin(1) #file type
fdata += toTapBin(1) + toTapBin(8) #starting address
fdata += toTapBin((blen+2049)%256) + toTapBin((blen+2049)/256) #ending address
for i in "DATA": fdata += toTapBin(ord(i)) #title
for i in range(12): fdata += toTapBin(32) #title padding
for i in range(171): fdata += toTapBin(32) #header body
fdata += toTapBin(1^1^8^((blen+2049)%256)^((blen+2049)/256)^68^65^84^65^0^32) #checksum
fdata += l+s #block end
ftemp += fdata #append header1 info
for i in range(79): ftemp += s #interblock gap
for i in range(9,0,-1): ftemp += toTapBin(i) #header2 sync
ftemp += fdata #append header2 info
for i in range(78): ftemp += s #header file end trailer
for i in range(5376): ftemp += s #interrecord gap
for i in range(9,0,-1): ftemp += toTapBin(128+i) #body1 sync
fdata = ""
for i in basic: fdata += toTapBin(i) #write memory data
g = 0
for i in basic: g ^= i #generate checksum
fdata += toTapBin(g) #check byte
fdata += l+s #block end
ftemp += fdata #append body1 info
for i in range(79): ftemp += s #interblock gap
for i in range(9,0,-1): ftemp += toTapBin(i) #body2 sync
ftemp += fdata #append body2 info
for i in range(78): ftemp += s #body file end trailer
for i in range(4): fcont += chr((len(ftemp)/(256**i))%256) #write file size
fcont += ftemp #attach data

f = open("data.tap","w")
f.write(fcont)
f.close()

