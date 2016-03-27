#!/usr/bin/env python
f = open("tapdump.txt","r")
p = f.read()
f.close()

count = 0 #simulate digitalRead function
def digitalRead():
	global count
	if count < len(p):
		tmp = p[count]
		count += 1
		return int(tmp)
	else: return 0

while digitalRead() == 0: pass #wait until signal starts, use this for motor
for x in range(1000): digitalRead() #skip first few small pulses, this is a delay
while digitalRead() == 1: pass #delay incase stopped in middle of small pulse
while digitalRead() == 0: pass #remove second half of pulse

def psize(): #algorithm to measure distance between rising edges
	sze = 0
	while digitalRead() == 1: sze += 1
	while digitalRead() == 0: sze += 1
	return sze + 2 #account for 2 lost pulses after whiles

avg = 0
for x in range(1000): avg += psize() #synchronise timing for 1000 small pulses

s = avg/1000.0 #average size of small pulse
m = s*1.15 #med pulse is p>=1.15s and p<1.7s
l = s*1.7 #long pulse is p>=1.7s

def lms(): #returns pulses as L-2 M-1 S-0
	g = psize()
	if g>=l: return 2
	if g>=m: return 1
	return 0
def tonum(h): #takes one tap byte
	h = [str(y) for y in h[2:18]]
	b = ""
	for a in range(8): b = h[a*2] + b
	return int(b,2)
def toasc(g): #turns list of 210 to ascii
	temp = ""
	for a in range(len(g)/20):
		temp += chr(tonum(g[a*20:a*20+20]))
	return temp

while lms() != 2: pass #wait for header large pulse
for x in range(179+20): lms() #skip sync bytes and filetype
start = [] #start address
for x in range(40): start.append(lms())
end = [] #end address
for x in range(40): end.append(lms())
title = [] #file name
for x in range(320): title.append(lms())
for x in range(3517): lms() #skip rest of header
while lms() != 2: pass #wait for next header
for x in range(4045): lms() #skip next header

start = toasc(start)
end = toasc(end)

print
print "start",repr(start)
print "end  ",repr(end)
print "title",repr(toasc(title))

start = ord(start[1])*16+ord(start[0]) #turn start into number
end = ord(end[1])*16+ord(end[0]) #turn end into number

for x in range(5376): lms() #skip interrecord gap
while lms() != 2: pass #wait for body large pulse
for x in range(179): lms() #skip sync bytes
body = [] #file data
r = end - start #get length of data
for x in range(r*20): body.append(lms())

print "body ",repr(toasc(body))

cmds = ["END","FOR","NEXT","DATA","INPUT#","INPUT","DIM","READ","LET","GOTO","RUN","IF","RESTORE","GOSUB","RETURN","REM","STOP","ON","WAIT","LOAD","SAVE","VERIFY","DEF","POKE","PRINT#","PRINT","CONT","LIST","CLR","CMD","SYS","OPEN","CLOSE","GET","NEW","TAB(","TO","FN","SPC(","THEN","NOT","STEP","+","-","*","/","^","AND","OR",">","=","<","SGN","INT","ABS","USR","FRE","POS","SQR","RND","LOG","EXP","COS","SIN","TAN","ATN","PEEK","LEN","STR$","VAL","ASC","CHR$","LEFT$","RIGHT$","MID$","GO"]
def topetscii(h):
	if h > 31 and h < 91:
		return chr(h)
	elif h > 127 and h < 204:
		return cmds[h-128]
	else: return "N"+str(h)
for x in toasc(body): print ord(x),"\t",topetscii(ord(x))
print

#start serial transmission
