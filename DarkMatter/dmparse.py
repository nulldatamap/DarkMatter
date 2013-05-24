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

# =========== PRECEDENCE TABLE ============
# expression | ( ) [ ] .
# unary		 | x++ x-- ++x --x !x ~x x as y @ & sizeof
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
			self.nextif( "SEMICOLON" )
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
		
	def expression(self):
		#= += -= *= /= %= &= ^= |= <<= >>= ~=
		tks = [ "ASSIGN" , "ADDASSIGN" , "SUBASSIGN" , "MULASSIGN" , "DIVASSIGN" , "MODASSIGN" , "ANDASSIGN" , "XORASSIGN" , 
		"ORASSIGN" , "NOTASSIGN" ];
		ops = [ "=" , "+=" , "-=" , "*=" , "/=" , "%=" , "&=" , "^=" , "|=" , "~=" ];
		tk = self.ternary();
		for i in range( len( tks ) ):
			if self.nextif( tks[ i ] ):
				return ASTObject( "op" , left=tk , op=ops[ i ] , right=self.assignment() );
		return tk;
		
	def ternary(self):
		tk = self.bop();
		if self.nextif( "QUEST" ):
			iftrue = self.expression();
			self.expect( "COLON" );
			iffalse = self.expression();
			return ASTObject( "ternary" , condition=tk , iftrue=iftrue , iffalse=iffalse );
		return tk;
	
	def bop( self ):
		# & ^ | && and || or
		tk = self.shiftcomp();
		if self.nextif( "AND" ):
			return ASTObject( "op" , left=tk , op="&" , right= self.bop() );
		if self.nextif( "XOR" ):
			return ASTObject( "op" , left=tk , op="^" , right= self.bop() );
		if self.nextif( "OR" ):
			return ASTObject( "op" , left=tk , op="|" , right= self.bop() );
		if self.nextif( "LOGICAND" ):
			return ASTObject( "op" , left=tk , op="&&" , right= self.bop() );
		if self.nextif( "LOGICOR" ):
			return ASTObject( "op" , left=tk , op="||" , right= self.bop() );
		return tk;
		
	def shiftcomp( self ):
		tk =  self.add();
		if self.nextif( "LSHIFT" ):
			return ASTObject( "op" , left=tk , op="<<" , right= self.shiftcomp() );
		if self.nextif( "RSHIFT" ):
			return ASTObject( "op" , left=tk , op=">>" , right= self.shiftcomp() );
		if self.nextif( "SSHIFT" ):
			return ASTObject( "op" , left=tk , op=">>>" , right= self.shiftcomp() );
		if self.nextif( "OANGL" ):
			return ASTObject( "op" , left=tk , op="<" , right= self.shiftcomp() );
		if self.nextif( "CANGL" ):
			return ASTObject( "op" , left=tk , op=">" , right= self.shiftcomp() );
		if self.nextif( "LESSEQL" ):
			return ASTObject( "op" , left=tk , op="<=" , right= self.shiftcomp() );
		if self.nextif( "GREATEQL" ):
			return ASTObject( "op" , left=tk , op=">=" , right= self.shiftcomp() );
		if self.nextif( "EQL" ):
			return ASTObject( "op" , left=tk , op="==" , right= self.shiftcomp() );
		if self.nextif( "NOTEQL" ):
			return ASTObject( "op" , left=tk , op="!=" , right= self.shiftcomp() );
		return tk;
	
	def add( self ):
		tk = self.mult();
		if self.nextif( "ADD" ):
			ast = ASTObject( "op" , left=tk , op="+" , right= self.add() );
			return ast;
		if self.nextif( "SUB" ):
			ast = ASTObject( "op" , left=tk , op="-" , right= self.add() );
			return ast;
		return tk;
	
	def mult( self ):
		tk = self.unary();
		if self.nextif( "MUL" ):
			ast = ASTObject( "op" , left=tk , op="*" , right= self.mult() );
			return ast;
		if self.nextif( "DIV" ):
			ast = ASTObject( "op" , left=tk , op="/" , right= self.mult() );
			return ast;
		if self.nextif( "MOD" ):
			ast = ASTObject( "op" , left=tk , op="%" , right= self.mult() );
			return ast;
		return tk;
		
	def unary( self ):
		# x++ x-- ++x --x !x ~x x as y @ & sizeof
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "++x", var= self.unary() );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "--x", var= self.unary() );
		if self.nextif( "EXCLA" ):
			return ASTObject( "op" , op= "!", var= self.unary() );
		if self.nextif( "TILDE" ):
			return ASTObject( "op" , op= "~", var= self.unary() );
		if self.nextif( "AND" ):
			return ASTObject( "op" , op= "addr", var= self.unary() );
		if self.nextif( "AT" ):
			return ASTObject( "op" , op= "@", var= self.unary() );
		if self.nextif( "SIZEOF" ):
			return ASTObject( "op" , op= "sizeof", var= self.unary() );
		tk = self.term();
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "x++", var= self.unary() );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "x--", var= self.unary() );
		if self.nextif( "AS" ):
			return ASTObject( "op" , op= "as", var= self.unary() , type= self.expect( "IDENT" ) );
	
	def term( self ):
		# function(  )
		tk = self.matches( "IDENT" ) and self.lookaheadmatches( "OPAREN" );
		if tk:
			tk = self.next();
			ast = ASTObject( "functioncall" , name=tk.data , arguments=[] );
			self.next();
			st = not self.matches( "CPAREN" );
			while st:
				ast.arguments.append( self.expression(  ) )
				if not self.nextif( "COMMA" ):
					break;
			self.expect( "CPAREN" , "')'" )
			p = self.prop( ast );
			if p:
				return p;
			return ast;
		# array[ expr ]
		tk = self.matches( "IDENT" ) and self.lookaheadmatches( "OBRKT" );
		if tk:
			tk = self.next();
			ast = ASTObject( "arrayindex" , name=tk.data , index=None );
			self.next();
			ast.index = self.expression();
			self.expect( "CBRKT" , "']'" )
			p = self.prop( ast );
			if p:
				return p;
			return ast;
		# ( expr )
		if self.nextif( "OPAREN" ):
			ast = self.expression();
			self.expect( "CPAREN" , "')'" );
			p = self.prop( ast );
			if p:
				return p;
			return ast;
		# var
		tk = self.nextif( "IDENT" );
		if tk:
			ast = ASTObject( "var" , name=tk.data );
			p = self.prop( ast );
			if p:
				return p;
			return ast
		try:
			l = self.literal()
			return l;
		except ParserError:
			raise ParserError( self.cur() , "a valid variable name or literal" );
			
	def prop( self , ownerr ):
		top = None;
		ast = ASTObject( "property" , owner=ownerr , property="" );
		if self.nextif( "DOT" ):
			tk = self.expect( "IDENT" );
			ast.property = tk.data;
			top = self.prop( ast );
			if top:
				return top;
			return ast;
		else:
			return False;
