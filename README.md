# C64Net
Repo for Commodore 64 Arduino Internet Project

This project is being made for my entry in the University of La Verne's Inaugural Mini Maker Fair.
I will attempt to give a Commodore 64 microcomputer internet access through the cassette port using an Arduino microcontroller
and a Linux laptop by bitbanging the cassette protocol.

Many of these files are simply proof of concept and aren't actually used for the main project.
Useful files:

Proof of concept files:
tapwriter.py - generates a tap file from C64 Basic input.
tapdump.txt - raw dump from an Arduino digital logic analyzer of the tape port's output.
readpulse.py - simulated tape port read routine written in Python.

Useful files:
c64net/c64net.ino - Arduino sketch to read from tape port (writing to tape port didn't work).
c64net/c64net.py - Python script to bridge Arduino and Twitter (writing to C64 disabled).

For more cool things, visit my blog at http://koppanyhorvath.blogspot.com/
