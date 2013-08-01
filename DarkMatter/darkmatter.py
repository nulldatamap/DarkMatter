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
import dmcsa

def readfile( filename ):
	readfile = open( filename , "r" );
	data = readfile.read();
	readfile.close();
	return data;
	
def writefile( filename , data ):
	writefile = open( filename , "w" );
	writefile.write( data );
	writefile.close();
	
def opToString( op ):
	l = "";
	r = "";
	if op.left.type == "op":
		l = opToString( op.left );
	elif op.left.type == "var":
		l =op.left.name;
	elif op.left.type == "literal":
		l = str( op.left.value );
	else:
		l = str( op.left );
	if op.right.type == "op":
		r = opToString( op.right );
	elif op.right.type == "var":
		r =op.right.name;
	elif op.right.type == "literal":
		r = str( op.right.value );
	else:
		r = str( op.right );
	return "( %s %s %s )" % ( l , op.op , r );

def stringifyPseudoCodeAtom( atom ):
	if atom.type == "var":
		return "$"+atom.name;
	elif atom.type == "literal":
		return str( atom.value );
	else:
		return str( atom )
	
def stringifyPseudoCode( pc ):
	out = "";
	for op in pc:
		args = "";
		for arg in op.args:
			args += stringifyPseudoCodeAtom( arg ) + " , ";
		args = args[:-3]
		#if op.haskey( "noret" ):
		#	nam = "";
		#else:
		#	nam = "$"+op.re.name+" = ";
		out += "%s %s\n" % (  op.type , args );
	return out;

def testrun():
	# Read the tokens and write them to a test file
	source = readfile( "../tests/testsource.dm" );
	lexer = dmlex.DMLexer();
	parser = dmparse.DMParser();
	tokens = lexer.lex( source );
	data = "";
	for token in tokens:
		#Write only the tokens that will be read
		if token.hidden == False and token.channel == 1:
			data += str( token ) + "\n";
	writefile( "../tests/testtokens.tok" , data );
	# Parse the tokens into an AST and write it to a file.
	ast = parser.parse( tokens );
	data = ""
	for st in ast:
		data += str( st ) + "\n";
	writefile( "../tests/testparse.ast" , data );
	# Resolve constants and save the map of them
	#data = "";
	#consts = dmcsa.createConstantMap( ast );
	#for k in consts.keys():
	#	data += "%s: %s\n"%( k , str( consts[k] ) );
	#writefile( "../tests/testconstants.dict" , data );
	#for statement in ast:
	#	dmcsa.analyseStatement( statement );
	#dmcsa.peephole();
	#print stringifyPseudoCode( dmcsa.pseudocode );
	

def printOp( data ):
	if data.type == "literal":
		return str( data.value )
	return "( %s %s %s )"%( printOp( data.left ) , data.op ,
		            		printOp( data.right ) );
	
	
def main( argv ):
	print """The DarkMatter compiler for the DCPU16.
	Written my Marco Aslak Persson.\n"""
	testrun(); # a temporary testing function

if __name__ == "__main__":
	main( sys.argv );

