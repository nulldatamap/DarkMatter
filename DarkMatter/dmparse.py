# Copyright (C) 2013	Marco Aslak Persson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>
#

# dmparse.py the parsing functions of the compiler


# THINGS TO DO:
# Make some scoping and variable declaration replacements

from IceLeaf import *
from dmcsa import SemanticError;

toplevelScope = {};
currentScope = toplevelScope;
scopeStack = [];

def declareName( name , var ):
	if currentScope.has_key( name ):
		raise SemanticError( "The name '%s' was already defined at %d:%d!" %
			                 ( name , currentScope[name].pos[0] ,
			                   currentScope[name].pos[1] ) );
	else:
		currentScope[name] = var;

def isDefined( name ):
	return currentScope.has_key( name );

def newScope():
  scopeStack.append( currentScope );
  currentScope = {};

def popScope():
  cs = currentScope;
  currentScope = scopeStack.pop();
  return cs;

class DMParser( Parser ):
	def __init__( self ):
		Parser.__init__( self );

	# ##################################
	# IT AIN'T BROKEN, SO DON'T FIX IT!!
	# ##################################
	#								 |
	#								 |
	#								 V

	def parse( self , tokens ):
		Parser.parse( self , tokens );
		# Skip past comments and newlines that the parser might start at
		self.skiptokens();
		exprs = [];
		while not self.matches( "EOF" ):
			v = self.toplevelcode();
			if v:
				exprs.append( v );
		return exprs;

	def literal( self ):
		tk = self.nextif( "NULL" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=0,
							  cast="pointer" , pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "TRUE" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=1,
							  cast="bool", pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "FALSE" );
		if tk:
			return ASTObject( "literal" , vtype="int", value=0,
							  cast="bool", pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "INT" );
		if tk:
			return ASTObject( "literal" , vtype="int", value= int( tk.data ),
							  cast="int", pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "OCT" );
		if tk:
			return ASTObject( "literal", vtype="int", value= int( tk.data , 8 ),
				   			  cast="uint", pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "HEX" );
		if tk:
			return ASTObject( "literal" , vtype="int" ,
							  value= int( tk.data[2:] , 16 ), cast="uint",
							  pos= ( tk.line , tk.pos ) );
		tk = self.nextif( "STRING" );
		if tk:
			v = tk.data[1:-1];
			v.replace( "\\\\" , "\\" );
			v.replace( "\\n" , "\n" );
			v.replace( "\\\"" , "\"" );
			v.replace( "\\'" , "'" );
			return ASTObject( "literal" , vtype="string" , value=v,
							  cast="string", pos= ( tk.line , tk.pos ) );
		raise ParserError( self.cur() , "a valid literal" );

	def expression(self):
		#= += -= *= /= %= &= ^= |= <<= >>= ~=
		tks = { "ASSIGN":"=" , "ADDASSIGN":"+=" , "SUBASSIGN":"-=" ,
			    "MULASSIGN":"*=" , "DIVASSIGN":"/=" , "MODASSIGN":"%=" ,
			    "ANDASSIGN":"&=" , "XORASSIGN":"^=" ,
				"ORASSIGN":"|=" , "NOTASSIGN":"~=" };
		tk = self.ternary();
		while self.cur().type in tks.keys():
			t = self.next().type;
			tk = ASTObject( "op" , left=tk , op=tks[t] ,
				            pos= ( self.cur().line , self.cur().pos ) ,
				            right= self.ternary() );
		return tk;

	def ternary(self):
		tk = self.bop();
		if self.nextif( "QUEST" ):
			iftrue = self.expression();
			pos = ( self.cur().line , self.cur().pos );
			self.expect( "COLON" );
			iffalse = self.expression();
			return ASTObject( "ternary" , condition=tk , iftrue=iftrue ,
							  iffalse=iffalse, pos= pos );
		return tk;

	def bop( self ):
		# & ^ | && and || or
		tks = { "AND":"&", "XOR":"^", "OR":"|", "LOGICAND":"&&",
				"LOGICOR":"||" };
		tk = self.shiftcomp();
		while self.cur().type in tks.keys():
			t = self.next().type;
			tk = ASTObject( "op" , left=tk , op=tks[t] ,
							pos= ( self.cur().line , self.cur().pos ) ,
							right= self.shiftcomp() );
		return tk;

	def shiftcomp( self ):
		tks = { "LSHIFT":"<<", "RSHIFT":">>", "OANGL":"<", "CANGL":">" ,
				"LESSEQL":"<=", "GREATEQL":">=", "EQL":"==", "NOTEQL":"!=" };
		tk = self.add();
		while self.cur().type in tks.keys():
			t = self.next().type;
			tk = ASTObject( "op" , left=tk , op=tks[t] ,
							pos= ( self.cur().line , self.cur().pos ),
							right= self.add() );
		return tk;

	def add( self ):
		tks = { "ADD":"+" , "SUB":"-" };
		tk = self.mult();
		while self.cur().type in tks.keys():
			t = self.next().type;
			tk = ASTObject( "op" , left=tk , op=tks[t] ,
							pos= ( self.cur().line , self.cur().pos ),
							right= self.mult() );
		return tk;

	def mult( self ):
		tks = { "MUL":"*" , "DIV":"/" , "MOD":"%" };
		tk = self.unary();
		while self.cur().type in tks.keys():
			t = self.next().type;
			tk = ASTObject( "op" , left=tk , op=tks[t] ,
							pos= ( self.cur().line , self.cur().pos ),
							right= self.unary() );
		return tk;

	def unary( self ):
		# x++ x-- ++x --x !x ~x x as y @ & sizeof
		if self.nextif( "SUB" ):
			return ASTObject( "op" , op="-x" ,
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "++x" ,
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "--x" ,
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "EXCLA" ):
			return ASTObject( "op" , op= "!" ,
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "TILDE" ):
			return ASTObject( "op" , op= "~" ,
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "ADDRESS" ):
			ast = ASTObject( "op" , op= "addr" ,
							 pos= ( self.cur().line , self.cur().pos ),
							 var= self.unary() );
			return ast;
		if self.nextif( "AT" ):
			return ASTObject( "op" , op= "@",
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		if self.nextif( "SIZEOF" ):
			return ASTObject( "op" , op= "sizeof",
							  pos= ( self.cur().line , self.cur().pos ),
							  var= self.unary() );
		tk = self.term();
		if self.nextif( "INC" ):
			return ASTObject( "op" , op= "x++",
							  pos= ( self.cur().line , self.cur().pos ),
							  var= tk );
		if self.nextif( "DEC" ):
			return ASTObject( "op" , op= "x--",
							  pos= ( self.cur().line , self.cur().pos ),
							  var= tk );
		if self.nextif( "AS" ):
			return ASTObject( "op" , op= "as",
							  pos= ( self.cur().line , self.cur().pos ),
							  var= tk , vtype= self.expect( "IDENT" ).data );
		return tk;

	def term( self ):
		# varname : type 
		if self.matches( "IDENT" ) and self.lookaheadmatches( "COLON" ):
			name = self.next();
			self.next(); # Skip the colon
			self.mark()
			ht = self.deftype();
			if ht:
				self.popmark();
				ast = ASTObject( "vardec" , vtype= ht ,
								 pos= ( name.line , name.pos ) ,
								 varname=name.data );
				declareName( ast.varname , ast );
				if self.nextif( "OBRKT" ):
					ast.vtype.isarray = True;
					ast.vtype.arraysize = self.expression();
					self.expect( "CBRKT" );
				return ASTObject( "var" , name= ast.varname , pos= ast.pos );
			else:
				self.restore();

		# structname{	}
		# structname{ field1= value , field2 = 10 }
		tk = self.matches( "IDENT" ) and self.lookaheadmatches( "OBRCE" );
		if tk:
			tk = self.next().data;
			self.next();
			ast = ASTObject( "structcontruct",
							 pos= ( self.cur().line , self.cur().pos ) ,
							 struct= tk , fields= {} );
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
			ast = ASTObject( "ramindex" ,
							 pos= ( self.cur().line , self.cur().pos ),
							 index=None );
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
			ast = ASTObject( "var" , pos= ( tk.line , tk.pos ), name=tk.data );
			p = self.sur( ast );
			if p:
				return p;
			return ast
		try:
			l = self.literal()
			return l;
		except ParserError:
			raise ParserError( self.cur(), "a valid variable name or literal");

	def sur( self , ownerr ):
		# .myvar.someothervarmaybe
		# expr[expr]
		top = None;
		if self.nextif( "DOT" ):
			ast = ASTObject( "property" ,
							 pos= ( self.cur().line , self.cur().pos ),
							 owner=ownerr , property="" );
			tk = self.expect( "IDENT" );
			ast.property = tk.data;
			top = self.sur( ast );
			if top:
				return top;
			return ast;
		if self.nextif( "OPAREN" ):
			ast = ASTObject( "functioncall" ,
							 pos= ( self.cur().line , self.cur().pos ),
							 owner= ownerr, arguments=[] );
			st = not self.matches( "CPAREN" );
			while st:
				ast.arguments.append( self.expression() );
				if not self.matches( "COMMA" ):
					break;
				self.next();
			self.expect( "CPAREN" );
			top = self.sur( ast );
			if top:
				return top;
			return ast;
		if self.nextif( "OBRKT" ):
			ast = ASTObject( "arrayindex" ,
							 pos= ( self.cur().line , self.cur().pos ),
							 owner=ownerr , index=self.expression() );
			self.expect( "CBRKT" );
			top = self.sur( ast );
			if top:
				return top;
			return ast;
		return False;

	#								 ^
	#								 |
	#								 |
	# ##################################
	# IT AIN'T BROKEN, SO DON'T FIX IT!!
	# ##################################

	def codestatement( self ):
		# <fine>
		if self.nextif( "LABEL" ):
			ast = ASTObject( "label" , name= self.expect( "IDENT" ).data ,
							 pos= ( self.cur().line , self.cur().pos ) );
			declareName( ast.name , ast );
			return ast;
		if self.nextif( "GOTO" ):
			return ASTObject( "gotostatement" ,
				              value= self.expect( "IDENT" ).data ,
				              pos= ( self.cur().line , self.cur().pos ) );
		if self.nextif( "CONTINUE" ):
			return ASTObject( "continuestatement" ,
							  pos= ( self.cur().line , self.cur().pos ) );
		if self.nextif( "BREAK" ):
			return ASTObject( "breakstatement" ,
							  pos= ( self.cur().line , self.cur().pos ) );
		if self.nextif( "RETURN" ):
			return ASTObject( "returnstatement" , value= self.expression() ,
							  pos= ( self.cur().line , self.cur().pos ) );
		# </fine>
		if self.nextif( "IF" ):
			ast = ASTObject( "ifstatement" , condition=self.expression() ,
				             iftrue= None , elsebody=None ,
				             pos= ( self.cur().line , self.cur().pos ) );
			code = ASTObject( "codeblock" , code= [] );
			ast.iftrue = code;
			self.nextif( "DO" ); # Loop ( loop while ) statements are allowed
			while not self.matches( "END" ) and not self.matches( "ELSE" ):
				c = self.code();
				if c:
					code.code.append( c );
				if self.matches( "EOF" ):
					raise ParserError( self.cur() , "'end' or 'else'" );
			if self.nextif( "ELSE" ):
				if self.matches( "IF" ):
					ast.elsebody = self.code();
				else:
					ast.elsebody = self.codeblock();
			else:
				self.expect( "END" , "'end'" );
			return ast;
		if self.nextif( "FOR" ):
			par = self.nextif( "OPAREN" )
			ast = ASTObject( "forloop" , init= self.peexpr() ,
							 condition= self.peexpr() , step= self.peexpr() ,
							 body= None , pos= ( self.cur().line ,
							 self.cur().pos ) );
			if par:
				self.expect( "CPAREN" , "')'" );
			ast.body = self.codeblock();
			return ast;
		if self.nextif( "WHILE" ):
			return ASTObject( "whileloop" , condition= self.peexpr() ,
							  body= self.codeblock() ,
							  pos= ( self.cur().line , self.cur().pos ) );
		if self.nextif( "LOOP" ):
			ast = ASTObject( "loopwhileloop" , condition= None ,
							 body= self.codeblock( "WHILE" ) ,
							 pos= ( self.cur().line , self.cur().pos ) );
			ast.condition = self.peexpr();
			return ast;
		if self.nextif( "REPEAT" ):
			ast = ASTObject( "repeatloop" , amount= self.expression() ,
						     body= None , withvar= None ,
						     pos= ( self.cur().line , self.cur().pos ) );
			if self.nextif( "WITH" ):
				ast.withvar = self.peexpr();
			ast.body = self.codeblock();
			return ast;
		if self.nextif( "SWITCH" ):
			ast = ASTObject( "switchstatement" , value= self.expression() ,
							 cases= [] , body= [] , defaultcase= None ,
							 pos= ( self.cur().line , self.cur().pos ) );
			self.expect( "OBRCE" );
			li = 0;
			cased = False;
			while not self.matches( "CBRCE" ):
				if self.nextif( "CASE" ):
					ast.cases.append( ASTObject( "case" ,
												 testvalue= self.term() ,
												 lineindex=li ,
												 pos= ( self.cur().line ,
												 	    self.cur().pos ) ) );
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

	
	#Stands for Possibly Empty EXPRession
	def peexpr( self ): 
		if self.nextif( "SEMICOLON" ) or self.matches( "EOF" ):
			return None;
		expr = self.expression();
		#Consume trailing semicolon. Just like all the other uses below
		self.nextif( "SEMICOLON" ); 
		return expr;

	# Fixed

	def deftype( self ):
		self.mark(); # in case of failed variable declaration
		ast = ASTObject( "deftype" , pointerdepth= 0 , isarray= False ,
						 arraysize= 0 , typename= "" ,
						 pos= ( self.cur().line , self.cur().pos ) );
		while self.nextif( "ADDRESS" ):
			ast.pointerdepth += 1;
		if not self.matches( "IDENT"):
			return None;
		ast.typename = self.nextif( "IDENT" ).data;
		while self.nextif( "OBRKT" ):
			if not self.nextif( "CBRKT" ):
				return None;
			# If we stack these up, only the last one has a meaning,
			# the rest is just the same as '#'
			ast.pointerdepth += 1;
			ast.isarray = True;
		if ast.isarray:
			ast.pointerdepth -= 1;
		return ast;

	# Should be fully working, no need for change

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

	# This is subject to change

	def codeblock( self , endkeyword= "END" ):
		ast = ASTObject( "codeblock" , code= [] , scope= newScope() );
		self.nextif( "DO" ); # Do statements are allowed
		while not self.matches( endkeyword ):
			c = self.code();
			if c:
				ast.code.append( c );
			if self.matches( "EOF" ):
				raise ParserError( self.cur() , "'%s'"%(endkeyword.lower()) );
		self.expect( endkeyword , "'%s'"%(endkeyword.lower()) );
		return ast;

	# Should be fully working, no need for change

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

	def functiondec( self ):
		# returntype , name , arguments ( argdef )
		if self.nextif( "FUNC" ):
			ast = ASTObject( "funcdec" ,
				             name= self.expect( "IDENT","function name" ).data ,
				             returntype= None , arguments= [] , body= None );
			declareName( ast.name , ast );
			# This function takes a number of arguments
			if self.nextif( "OPAREN" ):
				while not self.matches( "CPAREN" ):
					farg = ASTObject( "argdef" , name= "" , vartype= None );
					farg.name = self.expect( "IDENT" , "argument name" ).data;
					self.expect( "COLON" );
					at = self.deftype();
					if not at:
						raise ParserError( self.cur(),"a valid argument type" );
					self.popmark();
					farg.vartype = at;
					ast.arguments.append( farg );
					if not self.nextif( "COMMA" ):
						break;
				self.expect( "CPAREN" , "a closing parenthese" );
			if self.nextif( "ARROW" ): # The function will return something
				rt = self.deftype();
				if not rt:
					raise ParserError( self.cur() , "a valid return type" );
				self.popmark();
				ast.returntype = rt;
			ast.body = self.codeblock();
			return ast;
		return False;

	def structdec( self ):
		if self.nextif( "STRUCT" ):
			ast = ASTObject( "structdec" , name= self.expect( "IDENT" ).data );
			declareName( ast.name , ast );
			ast.type = "structdef";
			ast.fields = {};
			while not self.matches( "END" ):
				name = self.expect( "IDENT" ).data;
				self.expect( "COLON" );
				vt = self.deftype();
				if not vt:
					raise ParserError( self.cur() , "a valid type" );
				ast.fields[ name ] = vt;
				if self.nextif( "OBRKT" ):
					vt.isarray = True;
					vt.arraysize = self.expression();
					self.expect( "CBRKT" );
				self.nextif( "SEMICOLON" );
			self.expect( "END" );
			return ast;
		return False;


	def typedefdec( self ):
		if self.nextif( "TYPEDEF" ):
			ast = ASTObject( "typedef" , name= "" , vtype= self.deftype() );
			if not ast.vtype:
				raise ParserError( self.cur() , "a valid type" );
			self.popmark();
			ast.name = self.expect( "IDENT" ).data;
			declareName( ast.name , ast );
			return ast;
		return False;


	def constdef( self ):
		if self.nextif( "CONST" ):
			ast = ASTObject( "constdef" , name= "" , vtype= self.deftype() );
			if not ast.vtype:
				raise ParserError( self.cur() , "a valid type" );
			self.popmark();
			ast.name = self.expect( "IDENT" ).data;
			self.expect( "ASSIGN", "a value for the constant" );
			ast.value = self.expression();
			self.nextif( "SEMICOLON" );
			declareName( ast.name , ast );
			return ast;
		return False;

	# Should be fully working, no need for change

	def toplevelstatement( self ):
		# FUNCTION DECLARATION
		ast = self.functiondec();
		if ast:
			return ast;
		# STRUCTURE DECLARATION
		ast = self.structdec();
		if ast:
			return ast;
		# TYPEDEF DECLARATION
		ast = self.typedefdec();
		if ast:
			return ast;
		# CONSTANT DEFINITION
		ast = self.constdef();
		if ast:
			return ast;
		return None;
