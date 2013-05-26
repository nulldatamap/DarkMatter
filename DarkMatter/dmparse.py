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
			v = self.toplevelcode();
			if v:
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
		
	def expression(self):
		#= += -= *= /= %= &= ^= |= <<= >>= ~=
		tks = [ "ASSIGN" , "ADDASSIGN" , "SUBASSIGN" , "MULASSIGN" , "DIVASSIGN" , "MODASSIGN" , "ANDASSIGN" , "XORASSIGN" , 
		"ORASSIGN" , "NOTASSIGN" ];
		ops = [ "=" , "+=" , "-=" , "*=" , "/=" , "%=" , "&=" , "^=" , "|=" , "~=" ];
		tk = self.ternary();
		for i in range( len( tks ) ):
			if self.nextif( tks[ i ] ):
				return ASTObject( "op" , left=tk , op=ops[ i ] , right= self.expression() );
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
		if self.nextif( "SUB" ):
			return ASTObject( "op" , op="-x", var= self.unary() );
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "++x", var= self.unary() );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "--x", var= self.unary() );
		if self.nextif( "EXCLA" ):
			return ASTObject( "op" , op= "!", var= self.unary() );
		if self.nextif( "TILDE" ):
			return ASTObject( "op" , op= "~", var= self.unary() );
		if self.nextif( "AND" ):
			ast = ASTObject( "op" , op= "addr", var= self.unary() );
			if ast.var.type == "vardec" and ast.var.vtype.ispointer == False:
				ast.var.vtype.ispointer = True;
				return ast.var;
			return ast;
		if self.nextif( "AT" ):
			return ASTObject( "op" , op= "@", var= self.unary() );
		if self.nextif( "SIZEOF" ):
			return ASTObject( "op" , op= "sizeof", var= self.unary() );
		tk = self.term();
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "x++", var= tk );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "x--", var= tk );
		if self.nextif( "AS" ):
			return ASTObject( "op" , op= "as", var= tk , vtype= self.expect( "IDENT" ).data );
		return tk;
	
	def term( self ):
		# type varname ( aka. variable definition, this is not an expression for the sake of ease )
		self.mark()
		ht = self.deftype();
		if ht and self.matches( "IDENT" ):
			self.popmark();
			ast = ASTObject( "vardec" , vtype= ht , varname=self.next().data );
			if self.nextif( "OBRKT" ):
				ast.vtype.isarray = True;
				ast.vtype.arraysize = self.expression();
				self.expect( "CBRKT" );
			return ast;
		else:
			self.restore();
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
			p = self.sur( ast );
			if p:
				return p;
			return ast;
		# structname{  }
		# structname{ field1= value , field2 = 10 }
		tk = self.matches( "IDENT" ) and self.lookaheadmatches( "OBRCE" );
		if tk:
			tk = self.next().data;
			self.next();
			ast = ASTObject( "structcontruct" , struct= tk , fields= {} );
			while not self.matches( "CBRCE" ):
				fn = self.expect( "IDENT" ).data;
				self.expect( "ASSIGN" , "'='" );
				ast.fields[ fn ] = self.expression();
				if not self.nextif( "COMMA" ):
					break;
			self.expect( "CBRCE" , "'}'" );
			return ast;
		# [ expr ] 
		if self.matches( "OBRKT" ):
			ast = ASTObject( "ramindex" , index=None );
			self.next();
			ast.index = self.expression();
			if self.nextif( "COMMA" ):
				ast.type = "arrayliteral"
				ast.values = [ ast.index ];
				while not self.nextif( "CBRKT" ):
					ast.values.append( self.expression() );
					self.nextif( "COMMA" );
				return ast;
			self.expect( "CBRKT" , "']'" )
			return ast;
		# ( expr )
		if self.nextif( "OPAREN" ):
			ast = self.expression();
			self.expect( "CPAREN" , "')'" );
			p = self.sur( ast );
			if p:
				return p;
			return ast;
		# var
		tk = self.nextif( "IDENT" );
		if tk:
			ast = ASTObject( "var" , name=tk.data );
			p = self.sur( ast );
			if p:
				return p;
			return ast
		try:
			l = self.literal()
			return l;
		except ParserError:
			raise ParserError( self.cur() , "a valid variable name or literal" );
			
	def sur( self , ownerr ):
		# .myvar.someothervarmaybe
		# expr[expr]
		top = None;
		if self.nextif( "DOT" ):
			ast = ASTObject( "property" , owner=ownerr , property="" );
			tk = self.expect( "IDENT" );
			ast.property = tk.data;
			top = self.sur( ast );
			if top:
				return top;
			return ast;
		if self.nextif( "OBRKT" ):
			ast = ASTObject( "arrayindex" , owner=ownerr , index=self.expression() );
			self.expect( "CBRKT" );
			top = self.sur( ast );
			if top:
				return top;
			return ast;
		return False;
	
	def codestatement( self ):
		if self.matches( "IDENT" ) and self.lookaheadmatches( "COLON" ):
			ast = ASTObject( "label" , name= self.next().data );
			self.next();
			return ast;
		if self.nextif( "CONTINUE" ):
			return ASTObject( "continuestatement" );
		if self.nextif( "BREAK" ):
			return ASTObject( "breakstatement" );
		if self.nextif( "RETURN" ):
			return ASTObject( "returnstatement" , value= self.expression() );
		if self.nextif( "IF" ):
			ast = ASTObject( "ifstatement" , condition=self.expression()  , iftrue= self.codeblock() , elsebody=None );
			if self.nextif( "ELSE" ):
				ast.elsebody = self.codeblock();
			return ast;
		if self.nextif( "FOR" ):
			par = self.nextif( "OPAREN" )
			ast = ASTObject( "forloop" , init= self.peexpr() , condition= self.peexpr() , step= self.peexpr() , body= None );
			if par:
				self.expect( "CPAREN" , "')'" );
			ast.body = self.codeblock();
			return ast;
		if self.nextif( "WHILE" ):
			return ASTObject( "whileloop" , condition= self.peexpr() , body= self.codeblock() );
		if self.nextif( "DO" ):
			ast = ASTObject( "dowhileloop" , condition= None , body= self.codeblock() );
			self.expect( "WHILE" );
			ast.condition = self.peexpr();
			return ast;
		if self.nextif( "REPEAT" ):
			ast = ASTObject( "repeatloop" , amount= self.expression() , body= None , withvar= None );
			if self.nextif( "WITH" ):
				ast.withvar = self.peexpr();
			ast.body = self.codeblock();
			return ast;
		if self.nextif( "SWITCH" ):
			ast = ASTObject( "switchstatement" , value= self.expression() , cases= [] , body= [] , defaultcase= None );
			self.expect( "OBRCE" );
			li = 0;
			cased = False;
			while not self.matches( "CBRCE" ):
				if self.nextif( "CASE" ):
					ast.cases.append( ASTObject( "case" , testvalue= self.term() , lineindex=li ) );
					self.expect( "COLON" );
				if self.nextif( "DEFAULT" ):
					ast.defaultcase = li;
					self.expect( "COLON" );
				tk = self.code();
				if tk:
					li += 1;
					ast.body.append( tk );
			self.expect( "CBRCE" );
			return ast;
		return None;
	
	def peexpr( self ): #Stands for Possibly Empty EXPRession ( aka an expression or a semicolon instead )
		if self.nextif( "SEMICOLON" ) or self.matches( "EOF" ):
			return None;
		expr = self.expression();
		self.nextif( "SEMICOLON" ); #Consume trailing semicolon. Just like all the other uses below
		return expr;
	
	def deftype( self ):
		self.mark();
		ast = ASTObject( "deftype" , ispointer= False , isarray = False , arraysize=0 , typename= "" );
		if self.nextif( "AND" ):
			ast.ispointer = True;
		if self.matches( "IDENT" ):
			ast.typename = self.next().data;
		else:
			self.restore();
			return None;
		if self.nextif( "OBRKT" ):
			if not self.nextif( "CBRKT" ):
				self.restore();
				return None;
			ast.isarray = True;
		return ast;
	
	def code( self ):
		if self.nextif( "SEMICOLON" ) or self.matches( "EOF" ):
			return None;
		smt = self.codestatement();
		if smt:
			self.nextif( "SEMICOLON" )
			return smt;
		expr = self.expression();
		self.nextif( "SEMICOLON" )
		return expr;
	
	def codeblock( self , curlblock= False ):
		ast = ASTObject( "codeblock" , code= [] );
		if self.nextif( "OBRCE" ):
			while not self.matches( "CBRCE" ):
				c = self.code();
				if c:
					ast.code.append( c );
				if self.matches( "EOF" ):
					raise ParserError( self.cur() , "'}'" );
			self.expect( "CBRCE" , "'}'" );
			return ast;
		elif curlblock:
			raise ParserError( self.cur() , "a valid code block" );
		else:
			try:
				return self.code();
			except:
				raise ParserError( self.cur() , "a valid code block or code line" )
				
	def toplevelcode( self ):
		if self.nextif( "SEMICOLON" ) or self.matches( "EOF" ):
			return None;
		smt = self.toplevelstatement();
		if smt:
			self.nextif( "SEMICOLON" );
			return smt;
		smt = self.codestatement();
		if smt:
			self.nextif( "SEMICOLON" )
			return smt;
		expr = self.expression();
		self.nextif( "SEMICOLON" )
		return expr;
	
	def toplevelstatement( self ):
		self.mark()
		ht = self.deftype();
		if ht and self.matches( "IDENT" ) and self.lookaheadmatches( "OPAREN" ):
			self.popmark();
			ast = ASTObject( "functiondec" , returntype= ht , name= self.next().data , arguments= [] );
			self.next();
			while not self.matches( "CPAREN" ):
				vt = self.deftype();
				if not vt:
					raise ParserError( self.cur() , "a valid type" );
				av = ASTObject( "argdef" , vtype= vt , name= self.expect( "IDENT" ).data );
				ast.arguments.append( av );
				if not self.nextif( "COMMA" ):
					break;
			self.expect( "CPAREN" , "')'" )
			if self.matches( "OBRCE" ):
				ast.type = "functiondef";
				ast.body = self.codeblock( True );
			return ast;
		else:
			self.restore();
		if self.nextif( "STRUCT" ):
			ast = ASTObject( "structdec" , name= self.expect( "IDENT" ).data );
			if self.nextif( "OBRCE" ):
				ast.type = "structdef";
				ast.fields = {};
				while not self.matches( "CBRCE" ):
					vt = self.deftype();
					if not vt:
						raise ParserError( self.cur() , "a valid type" );
					ast.fields[ self.expect( "IDENT" ).data ] = vt;
					if self.nextif( "OBRKT" ):
						vt.isarray = True;
						vt.arraysize = self.expression();
						self.expect( "CBRKT" );
					self.nextif( "SEMICOLON" );
				self.expect( "CBRCE" );
			return ast;
		if self.nextif( "TYPEDEF" ):
			ast = ASTObject( "typedef" , name= "" , vtype= self.deftype() );
			if not ast.vtype:
				raise ParserError( self.cur() , "a valid type" );
			ast.name = self.expect( "IDENT" ).data;
			return ast;
		if self.nextif( "CONST" ):
			ast = ASTObject( "constdef" , name= "" , vtype= self.deftype() );
			if not ast.vtype:
				raise ParserError( self.cur() , "a valid type" );
			ast.name = self.expect( "IDENT" ).data;
			self.expect( "ASSIGN", "a value for the constant" );
			ast.value = self.expression();
			self.nextif( "SEMICOLON" );
			return ast;
		return None;
			