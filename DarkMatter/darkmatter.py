# Copyright (C) 2013  Marco Aslak Persson
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

# darkmatter.py the compiler for DarkMatter

import sys
import dmlex
import dmparse
import dmast

def readfile( filename ):
	readfile = open( filename , "r" );
	data = readfile.read();
	readfile.close();
	return data;
	
def writefile( filename , data ):
	writefile = open( filename , "w" );
	writefile.write( data );
	writefile.close();

def testrun():
	source = readfile( "../tests/testsource.dm" );
	lexer = dmlex.DMLexer();
	parser = dmparse.DMParser();
	tokens = lexer.lex( source );
	data = "";
	extra = "";
	for token in tokens:
		if token.hidden == False and token.channel == 1: #Write only the tokens that will be read
			data += str( token ) + "\n";
	writefile( "../tests/testtokens.tok" , data );
	ast = parser.parse( tokens );
	data = ""
	for st in ast:
		data += str( st ) + "\n";
#		if st.type == "op":
#			extra += printOp( st ) + "\n";
	writefile( "../tests/testparse.ast" , data+extra );

def printOp( data ):
	if data.type == "literal":
		return str( data.value )
	return "( %s %s %s )"%( printOp( data.left ) , data.op , printOp( data.right ) );
	
	
def main( argv ):
	print "The DarkMatter compiler for the DCPU16.\nWritten my Marco Aslak Persson.\n"
	testrun(); # a temporary testing function

if __name__ == "__main__":
	main( sys.argv );

