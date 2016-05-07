#!/usr/bin/env python
import serial, os, twitter
from time import sleep

cmds = ["END","FOR","NEXT","DATA","INPUT#","INPUT","DIM","READ","LET","GOTO","RUN","IF","RESTORE","GOSUB","RETURN","REM","STOP","ON","WAIT","LOAD","SAVE","VERIFY","DEF","POKE","PRINT#","PRINT","CONT","LIST","CLR","CMD","SYS","OPEN","CLOSE","GET","NEW","TAB(","TO","FN","SPC(","THEN","NOT","STEP","+","-","*","/","^","AND","OR",">","=","<","SGN","INT","ABS","USR","FRE","POS","SQR","RND","LOG","EXP","COS","SIN","TAN","ATN","PEEK","LEN","STR$","VAL","ASC","CHR$","LEFT$","RIGHT$","MID$","GO"] #list of basic commands
t = twitter.Twitter(auth=twitter.OAuth("token",
	"token_key",
	"con_secret",
	"con_secret_key"))
serial.Serial("/dev/ttyUSB0",9600) #need this to work
ser = serial.Serial("/dev/ttyUSB0",230400)

def getTap(): #returns the serial tap data from the c64
	print "Ready for SAVE..."
	start = ord(ser.read(1))
	start += ord(ser.read(1))*256
	end = ord(ser.read(1))
	end += ord(ser.read(1))*256
	title = ser.read(16)
	data = ""
	for x in range(end-start+1): data += ser.read(1)
	data = data[1:]
	return (start, end, title, data)
#def sendTap((start,end,title,data)): #sends tap data to c64
#	print "LOAD"
#	ser.write(chr(start & 255))
#	ser.write(chr(start / 256))
#	ser.write(chr(end & 255))
#	ser.write(chr(end / 256))
#	ser.write(title)
#	for y in data: ser.write(y)
def parseTap(g): #returns raw c64 tap data concatenated w/o addresses and 0's
	k = ""
	while len(g) > 3:
		g = g[4:]
		n = 0
		for y in g:
			n += 1
			if(y == "\x00"): break
			b = ord(y)
			if b == 92: k += "\n"
			elif b>31 and b<97: k += y
			elif b>127 and b<204: k += cmds[b-128]
		g = g[n:]
	return k
#def getWeb(g): #returns webpage formatted in 38x23 width in C64 pgm
#	print "Downloading "+g
#	g = os.popen("lynx -dump "+g).read()
#	s = []
#	##############work on this
##	n = 0
##	for y in x.split("\n"):
##		for j in range(int(len(y)/38.0+1)):
##			s.append(y[n:n+38])
##			n += 38
##		n = 0

##	for y in g[:23]: print y
#	return g
def tweet(g): #update twitter status
	t.statuses.update(status=g)

#for x in range(1):
while 1:
	try: a = getTap()
	except: ser.close; exit()
	
	print a[0] #start
	print a[1] #end
	print a[2] #title
	print repr(a[3]) #data
	
	fs = a[2].strip()
	if fs == "TWEET":
		print "ACTION: Tweet"
		tweet(parseTap(a[3]))
	elif fs == "PRINT":
		print "ACTION: Print"
		print parseTap(a[3])
	elif fs in ["EXIT","QUIT"]: #exit command
		print "Exiting..."
		ser.close()
		exit()
	elif fs == "HELP":
		print "\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		print "Type each line separately starting with a number and incrementing. E.G.:"
		print "0 THIS IS A TWEET FROM A C64 BU"
		print "1 T LINE WRAPPING IS MANUAL WIT"
		print "2 INCREASING NUMBERS"
		print "\nCommands are: TWEET, PRINT, EXIT, HELP"
		print "The Pound symbol is the ascii new line symbol"
		print "\nMade by Koppany Horvath for the University of La Verne Mini Maker Fair"
		print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	else: print parseTap(a[3])
	print
	
	#######################
	
#	sleep(5)
#	#a = (0,0,"DATA            ",'\x00\x00\x00')
#	a = (3072, 3072 + a[1]-a[0], a[2], a[3])
#	sendTap(a)
	
