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

# dmparse.py the parsing functions of the compiler

from IceLeaf import *
from dmast import ASTObject

# =========== PRECEDENCE TABLE ============
# expression | ( ) [ ] . x++ x-- ++x --x !x ~x x as y @ & sizeof
# mult       | * / %
# add        | + -
# shiftcomp  | << >> >>> < <= > >= == != <>
# bop        | & ^ | && and || or
# ternary    | ?:
# assignment | = += -= *= /= %= &= ^= |= <<= >>= ~=
# term       | literal IDENT


class DMParser( Parser ):
	def __init__( self ):
		Parser.__init__( self );
	
	def parse( self , tokens ):
		Parser.parse( self , tokens );
		self.skipTokens(); # Skip past comments and newlines that the parser might start at
		exprs = [];
		while not self.matches( "EOF" ):
			v = self.expression();
			exprs.append( v )
		return exprs;
	
	def literal( self ):
		tk = self.nextif( "NULL" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=0 )
		tk = self.nextif( "TRUE" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=1 )
		tk = self.nextif( "FALSE" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=0 )
		tk = self.nextif( "INT" );
		if tk:
			return ASTObject( "literal" , vtype="int", value= int( tk.data ) )
		tk = self.nextif( "OCT" );
		if tk:
			return ASTObject( "literal" , vtype="int", value= int( tk.data , 8 ) )
		tk = self.nextif( "HEX" );
		if tk:
			return ASTObject( "literal" , vtype="int" , value= int( tk.data[2:] , 16 ) );
		tk = self.nextif( "STRING" );
		if tk:
			v = tk.data[1:-1];
			v.replace( "\\\\" , "\\" );
			v.replace( "\\n" , "\n" );
			v.replace( "\\\"" , "\"" );
			v.replace( "\\'" , "'" );
			return ASTObject( "literal" , vtype="string" , value=v );
		raise ParserError( self.cur() , "a valid literal" );
	
	def expression( self ):
		return self.mult();
		
	def mult( self ):
		return self.add();
		
	def add( self ):
		return self.shiftcomp();
		
	def shiftcomp( self ):
		return self.bop();
		
	def bop( self ):
		return self.ternary();
		
	def ternary(self):
		return self.assigment();
		
	def assigment(self):
		return self.term();
	
	def term(self):
		tk = self.nextif( "IDENT" );
		if tk:
			return ASTObject( "var" , name=tk.data );
		try:
			return self.literal();
		except ParserError:
			raise ParserError( self.cur() , "a valid variable name or literal" );
	
