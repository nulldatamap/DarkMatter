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

# dmast.py the AST functions of the compiler

from IceLeaf import ASTObject;

class SemanticError( Exception ):
	def __init__( self , msg ):
		self.message = msg;
		
	def __str__( self ):
		return "Semantic error: " + self.message;


types = [ "bool" , "int" , "uint" , "char" , "pointer" , "func" ];

expressionTypes = [ "ternary" , "op" , "vardec" , "functioncall" , "structcontruct" , "ramindex" , "var" , "property" , "arrayindex" , "literal" ];
nonConstantTypes = [ "functioncall" , "ramindex" , "property" , "arrayindex" , "vardec" , "structconstruct" ];

opLTR = [ "&" , "|" , "^" , "&&" , "||" , "<<" , ">>" , "<" , ">" , "==" , "<=" , ">=" , "!=" , "+" , "-" , "*" , "/" , "%" ];
opS = [ "-x" , "--x" , "++x" , "x--" , "x++" , "!" , "~" ];

# -- expressions	| CONST |
# literal			|   T   |
# ternary			|   ?   |
# vardec			|   F   |
# op				|   ?   |
# functioncall		|   F   |
# ramindex			|   F   |
# structcontruct	|   F   |
# property			|   F   |
# arrayindex		|   F   |
# var				|   F   |
# -- statements
# label
# gotostatement
# continuestatement
# breakstatement
# returnstatement
# ifstatement
# forloop
# whileloop
# dowhileloop
# repeatloop
# switchstatement
# case
# deftype
# codeblock
# -- toplevel statements
# functiondec
# argdef
# structdec
# constdef
# typedef

constmap = {};
typemap = { "int":None , "uint":None , "char":None , "bool":None , "pointer":None , "func":None };
globalvarmap = {};
tempcount = 0;
pseudocode = [];
useables = [];
registers = { "A":False,  "B":False , "C":False , "X":False , "Y":False , "Z":False , "I":False , "J":False };

def getSizeOf( value ):
	return None;

def createConstantMap( ast ):
	global constmap
	constmap = {};
	for atom in ast: # Round 1, gather constants
		if atom.type == "constdef":
			value = resolveConstant( atom.value );
			if not value:
				raise SemanticError( "Can not define a constant with a non-constant value! At %d:%d"%( atom.value.pos[0] , atom.value.pos[1] ) );
			constmap[ atom.name ] = value;
	return constmap;
	
# "&" , "|" , "^" , "&&" , "||" , "<<" , ">>" , "<" , ">" , "==" , "<=" , ">=" , "!=" , "+" , "-" , "*" , "/" , "%"
def resolveLTROperation( left , op , right ):
	if op == "+":
		if left.vtype == "string":
			if right.vtype == "int":
				left.value += chr( right.value );
				return left;
			if right.vtype == "string":
				left.value += right.value;
				return left;
		left.value += right.value;
		return left;
	if left.vtype == "string" or right.vtype == "string":
		raise SemanticError( "Can not perform \'"+op+"' operation on a string constant. At %d:%d"%( op.pos[0] , op.pos[1] ) );
	if op == "&":
		left.value &= right.value;
		return left;
	if op == "|":
		left.value |= right.value;
		return left;
	if op == "^":
		left.value ^= right.value;
		return left;
	if op == "&&":
		if left.value != 0 and right.value != 0:
			left.value = 1;
		else:
			left.value = 0;
		return left;
	if op == "||":
		if left.value != 0:
			left.value = 1;
		else:
			left.value = 0;
		return left;
	if op == "<<":
		left.value = ( left.value << right.value ) & 0xFFFF;
		return left;
	if op == ">>":
		if left.cast == "uint":
			left.value = ( left.value >> right.value ) & 0x7FFF;
		else:
			left.value = ( left.value << right.value ) & 0xFFFF;
		return left;
	if op == "<":
		if left.value < right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == ">":
		if left.value > right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == "==":
		if left.value == right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == "<=":
		if left.value <= right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == ">=":
		if left.value >= right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == "!=":
		if left.value != right.value:
			return ASTObject( "literal" , vtype= "int", value= 1, cast= "bool" );
		else:
			return ASTObject( "literal" , vtype= "int", value= 0, cast= "bool" );
	if op == "-":
		left.value -= right.value;
		return left;
	if op == "*":
		left.value *= right.value;
		return left;
	if op == "/":
		left.value /= right.value;
		return left;
	if op == "%":
		left.value %= right.value;
		return left;
	return None;
	
#  "-x" , "--x" , "++x" , "x--" , "x++" , "!" , "~"
def resolveSOperation( op , val ):
	if val.vtype == "string":
		raise SemanticError( "Can not perform \'"+op+"' operation on a string constant. At %d:%d"%( op.pos[0] , op.pos[1] ) );
	if op == "x--" or op == "x++":
		return val;
	if op == "-x":
		val.var = -val.var;
		return val;
	if op == "++x":
		val.var += 1;
		return val;
	if op == "--x":
		val.var -= 1;
		return val;
	if op == "!":
		if val.var == 0:
			val.var = 1;
		else:
			val.var = 0;
		return val;
	if op == "~":
		val.var = ~val.var;
		return val;

def resolveConstant( expr ):
	global constmap
	if expr.type == "var":
		if expr.name in constmap.keys():
			const = constmap[ expr.name ];
			expr.type = const.type;
			expr._data = const._data.copy();
		else:
			raise SemanticError( "No constant defined with the name '"+expr.name+"'. At %d:%d"%( expr.pos[0] , expr.pos[1] ) );
	if expr.type in nonConstantTypes:
		return None;
	if expr.type == "literal":
		expr.value &= 0xFFFF
		return expr;
	if expr.type == "ternary":
		cv = resolveConstant( expr.condition );
		if cv == None:
			return None;
		if cv == 0:
			return resovleConstant( expr.isfalse );
		else:
			return resolveConstant( expr.istrue );
	if expr.type == "op":
		if expr.op in opLTR:
			left = resolveConstant( expr.left  );
			right = resolveConstant( expr.right  );
			if left == None or right == None:
				return None;
			left.value &= 0xFFFF;
			right.value &= 0xFFFF;
			r = resolveLTROperation( left , expr.op , right );
			r.value &= 0xFFFF;
			return r;
		if expr.op in opS:
			value = resolveConstant( expr.value );
			if value == None:
				return None;
			value.value &= 0xFFFF;
			r = resolveSOperation( expr.op , value );
			r.value &= 0xFFFF;
			return r;
	return None;

def isConstant( expr ):
	global constmap
	if expr.type in nonConstantTypes:
		return False;
	if expr.type == "var":
		if expr.name in constmap.keys():
			return True;
		return False;
	if expr.type == "ternary":
		if isConstant( expr.condition ):
			try:
				tof = resolveConstant( expr.condition ); # There is a lot of things that can go wrong here, heh
			except:
				return False;
			if tof == None:
				return False;
			if tof != 0:
				return isConstant( expr.isture );
			else:
				return isConstant( expr.isfalse );
		return False;
	if expr.type == "op":
		if expr.type in opLTR:
			return isConstant( expr.left ) and isConstant( expr.right );
		if expr.type in opS:
			return isConstant( expr.var );
		return False;
	return True;

def resolveAtom( atom ):
	global constmap
	if not isConstant( atom ):
		print "Failed at %d:%d"%( atom.pos[0] , atom.pos[1] );
		return atom;
	var = resolveConstant( atom );
	if var == None:
		return atom;
	atom.type = var.type;
	atom._data = var._data.copy();

def resolveConstantExpressions( ast ):
	global constmap
	for atom in ast:
		if atom.type in expressionTypes:
			resolveAtom( atom );
	return ast;
	
def isVar( ast , varname ):
	return ast.type == "var" and ast.name == varname;
	
def treeToList( tree ):
	stack = [];
	rstack = [];
	stack.append( tree );
	while len( stack ) > 0:
		cur = stack.pop();
		rstack.append( cur );
		if cur.right.type == "op":
			stack.append( cur.right );
		if cur.left.type == "op":
			stack.append( cur.left );
	return rstack;
	
def opToPseudocode( op ):
	otp = { "=" : "@set" , "+" : "@add" , "-" : "@sub" , "*" : "@mul" , "/" : "@div" , "%" : "@mod" , "<<" : "@lshift" , ">>" : "@rshift" };
	return otp[op];
	
def pseudocodeToOp( psc ):
	pto = { '@sub': '-', '@set': '=', '@rshift': '>>', '@add': '+', '@lshift': '<<', '@mod': '%', '@div': '/', '@mul': '*' }; # generated with python because I'm lazy
	return ptp[op];
	
def spawnTempVar( bp=None ):
	global tempcount;
	if len( useables ) == 0:
		if bp:
			r = ASTObject( "var" );
			r._data = bp._data.copy();
			r.istemp = True;
			r.name = "_temp#"+str(tempcount);
		else:
			r = ASTObject( "var" , name= "_temp#"+str(tempcount) , istemp = True );
		tempcount += 1;
	else:
		r = useables.pop();
		if bp:
			c = bp._data.copy();
			c["istemp"] = True;
			c["name"] = r.name;
			r._data = c;
	pushCode( "@load" , copy( r ) );
	return r;
	
def findRegister(  ):
	global registers;
	for reg in sorted( registers.keys() ):
		if registers[reg] == False:
			return reg;
	return None;
	
def getRegister( var ):
	global registers;
	for reg in sorted( registers.keys() ):
		if registers[reg]:
			if isVar( registers[reg] , var ):
				return reg;
	return None;
	
def isPowerOfTwo( x ):
	if( x == 0 ):
		return 0;
	return x & ( x - 1 ) == 0;

def log2( v ): # Some bit hacking going on here, very clever ( I didn't come up with it )
	if v & 0xAAAAAAAA:
		r = 1;
	else:
		r = 0;
	if v & 0xFFFF0000:
		r |= 1 << 4;
	if v & 0xFF00FF00:
		r |= 1 << 3;
	if v & 0xF0F0F0F0:
		r |= 1 << 2;
	if v & 0xCCCCCCCC:
		r |= 1 << 1;
	return r;

def isOperation( part ):
	return part.type != "var" and part.type != "literal";
	
def countReferences( setroot ):
	stack = [];
	count = 0;
	if not isOperation( setroot.right ):
		return 0;
	stack.append( setroot.right );
	while len( stack ) > 0:
		cur = stack.pop();
		if isVar( cur.right , setroot.left.name ):
			count += 1;
		elif cur.right.type == "op":
			stack.append( cur.right );
		if cur.left.type == "op":
			stack.append( cur.left );
	return count;
	
def replaceVar( oper , varname , newname ):
	for arg in oper.args:
		if isVar( arg , varname ):
			arg.name = newname;
			
def pushCode( op , *args ):
	global pseudocode;
	pseudocode.append( ASTObject( op , args=args ) );
	
def copy( ast ):
	r = ASTObject( ast.type );
	r._data = ast._data.copy();
	return r;

def analyseStatement( statement ):
	global constmap , typemap , pseudocode , tempcount , useables;
	# Setup varaibles
	selfref = False;
	self = statement.left;
	stack = treeToList( statement );
	temps = {};
	resualts = {};
	ctemp = None;
	# 
	while len( stack ):
		operation = stack.pop();
		# Replace not self referencing temp variables with the setted variable itself
		if operation.op == "=" and countReferences( operation ) < 2 and isOperation( operation.right ):
			right = operation.right;
			if isOperation( right ):
				right = copy( resualts[right] );
			if right.type == "var" and right.haskey( "istemp" ):
				# It is being assigned to a temp variable, replace it with itself
				i = len( pseudocode );
				while i > 0:
					i -= 1;
					if pseudocode[i].type == "@load" and isVar( pseudocode[i].args[0] , right.name ):
						pseudocode.remove( pseudocode[i] );
						break;
					replaceVar( pseudocode[i] , right.name , operation.left.name );
				resualts[operation] = copy( operation.left );
		else:
			# Check for constant expressions
			if operation.left.type == "literal" and operation.right.type == "literal":
				resualts[operation] = resolveConstant( operation );
				continue;
			left = operation.left;
			right = operation.right;
			
			if isOperation( left ):
				left = copy( resualts[left] );
			if isOperation( right ):
				right = copy( resualts[right] );
			
			r = left;
			if operation.op != "=" and not left.haskey( "istemp" ):
				r = spawnTempVar( left );
				pushCode( "@set" , r , left );
				if left.haskey( "istemp" ):
					pushCode( "@unload" , copy( left ) );
					useables.append( left );
			pushCode( opToPseudocode( operation.op ) , copy( r ) , copy( right ) );
			
			if right.haskey( "istemp" ):
				pushCode( "@unload" , copy( right ) );
				useables.append( right );
			resualts[operation] = copy( r );
	return pseudocode;
	
def peephole():
	global pseudocode;
	# Check for self assignments
	npc = [];
	for i in range( len( pseudocode ) ):
		op = pseudocode[i];
		npc.append( op );
		if op.type == "@set" and op.args[1].type == "var" and isVar( op.args[0] , op.args[1].name ):
			npc.pop( );
	pseudocode = npc;
	# Check for zero add/sub
	npc = [];
	for i in range( len( pseudocode ) ):
		op = pseudocode[i];
		npc.append( op );
		if ( op.type == "@add" or op.type == "@sub" ) and op.args[1].type == "literal" and op.args[1].value == 0:
			npc.pop();
	pseudocode = npc;
	# Check for zero mul/div/mod
	npc = [];
	for i in range( len( pseudocode ) ):
		op = pseudocode[i];
		npc.append( op );
		if ( op.type == "@mul" or op.type == "@div" or op.type == "@mod" ) and op.args[1].type == "literal":
			if op.args[1].value == 0:
				npc[ len( npc ) - 1 ] = ASTObject( "@set" , args= op.args );
			elif op.args[1].value == 1 and op.type in [ "@div" , "@mul" ]:
				npc.pop();
	pseudocode = npc;
	# Check for negating actions
	opposideaction = { "@add":"@sub" , "@sub":"@add" , "@mul":"@div" , "@div":"@mul" , "xor":"xor" };
	i = 0;
	npc = [];
	while i < len( pseudocode ) - 1: # pseudocode[i+1] will always be valid in this while loop
		op = pseudocode[i];
		npc.append( op );
		if op.type in opposideaction:
			if pseudocode[i+1].type == opposideaction[op.type]:
				oop = pseudocode[i+1];
				if op.args[0].type == oop.args[0].type: # REMEMBER ADD TEST FOR RAM INDEXES
					if op.args[1].type == "literal" and oop.args[1].type == "literal" and op.args[1].value == oop.args[1].value:
						npc.pop();
						i += 1;
		i += 1;
	npc.append( pseudocode[-1] );
	pseudocode = npc;
	# Check for mul/div with the power for 2
	npc = [];
	for i in range( len( pseudocode ) ):
		op = pseudocode[i];
		npc.append( op );
		if op.type in [ "@mul" , "@div" ] and op.args[1].type == "literal" and isPowerOfTwo( op.args[1].value ):
			print "trueh"
			if op.type == "@mul":
				op.args[1].value = log2( op.args[1].value );
				npc[i] = ASTObject( "@lshift" , args= [ op.args[0] , op.args[1] ] );
			else:
				op.args[1].value = log2( op.args[1].value );
				npc[i] = ASTObject( "@rshift" , args= [ op.args[0] , op.args[1] ] );
	pseudocode = npc;
	# Check for constant operations
	# Check for unused load variables
	
