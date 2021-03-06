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
tempmap = {};
tempcount = 0;

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

def newtemp( cast = None ):
	global tempcount, tempmap;
	ret = ASTObject( "var" , name= "_temp#"+str(tempcount) , cast= cast , referencecount= 0 , references= [] , lastref= 0 )
	tempcount += 1;
	tempmap[ ret.name ] = ret;
	return ret;

def disassembleAtom( atom ):
	global pseudocode, tempcount;
	if atom.type == "op":
		ops = { "=":"@set" , "+":"@add" , "-":"@sub" , "*":"@mul" , "/":"@div" , "%":"@mod" , "<<":"@lshft" , ">>":"@rshft" };
		if atom.op in ops.keys():
			l = disassembleAtom( atom.left );
			r = disassembleAtom( atom.right );
			if l.type == "literal" and r.type == "literal":
				return resolveLTROperation( l , atom.op , r );
			ret = newtemp(  );
			if l.haskey( "cast" ):
				ret.cast = l.cast;
			#Case optimization
			if atom.op == "+" and r.type == "literal" and r.value <= 0:
				atom.op = "-";
				r.value = -r.value;
			if atom.op == "-" and r.type == "literal" and r.value <= 0:
				atom.op = "+";
				r.value = -r.value;
			#Resualt
			pc = ASTObject( ops[atom.op] , args = [ l , r ] , re = ret );
			pseudocode.append( pc );
			return ret;
	if atom.type == "literal":
		return atom;
	if atom.type == "var":
		if atom.name in typemap.keys():
			raise SemanticError( "Variable name '%s' already defined as a type. At %d:%d" % ( atom.name , atom.pos[0] , atom.pos[1] ) );
		if atom.name in constmap.keys():
			const = constmap[ atom.name ];
			atom.type = const.type;
			atom._data = const._data.copy();
		return atom;

def createPseudoCode( ast ):
	global pseudocode;
	pseudocode = [];
	for atom in ast:
		disassembleAtom( atom );
	return pseudocode;

def replaceChanLinks( link , replacement , v ):
	tv = link.re;
	if tv.name == replacement.name:
		return;
	for arg in link.args:
		if arg.type == "var" and arg.name == v.name:
			arg._data = replacement._data;
	for refer in tv.references:
		replaceChanLinks( refer , replacement , tv );
	link.re = replacement;
	
def resolveChain( link ):
	if link.referencecount != 0 and len( link.references ) == 1:
		ref = link.references[0];
		replaceChanLinks( ref , link , ref.re );

def fixPythonReferences( pc ):
	global tempmap;
	for op in pc:
		for arg in op.args:
			if arg.type == "var" and arg.name in tempmap.keys():
				arg._data = tempmap[ arg.name ]._data;
		if op.re.type == "var" and op.re.name in tempmap.keys():
			op.re._data = tempmap[ op.re.name ]._data;
		
def updateRefCounts( pc ):
	global tempmap;
	for k in tempmap.keys():
		v = tempmap[ k ];
		v.referencecount = 0;
		v.references = [];
		v.lastref = 0;
	for op in pc:
		for arg in op.args:
			if arg.type == "var" and arg.haskey( "referencecount" ):
				arg.referencecount += 1;
				if len( arg.references ) == 0 or arg.references[-1] != op:
					arg.references.append( op )
		
def optimizeFlow( pc ):
	global pseudocode, tempmap;
	pseudocode = pc;
	# Resolve useless temps and put temp vars into contex
	updateRefCounts( pc );
	for key in sorted( tempmap.keys() ):
		resolveChain( tempmap[ key ] );
	#fixPythonReferences( pc );
	updateRefCounts( pc );
	for op in pc:
		if op.re.referencecount == 0:
			op.noret = True;
		elif op.re.references[-1] == op:
			op.noret = True;
	# Seach for negating operations
	newpc = [];
	prev = None;
	negatables = { "@mul":"@div","@div":"@mul","@add":"@sub","@sub":"@mul" };
	for op in pc:
		if op.type in negatables.keys() and prev != None and prev.type == negatables[ op.type ]:
			if op.args[1].type == "literal" and prev.args[1].type == "literal":
				if op.args[1].value == prev.args[1].value:
					oldop = newpc.pop();
					newpc.append( ASTObject( "@set" , args= [ op.re , oldop.args[0] ]  , noret= True ) );
					continue;
		prev = op;
		newpc.append( op )
	pseudocode = newpc;
	return pseudocode;

def findRegister( op , registers ):
	if registers.A == op:
		return "A";
	if registers.B == op:
		return "B";
	if registers.C == op:
		return "C";
	if registers.I == op:
		return "I";
	if registers.J == op:
		return "J";
	if registers.X == op:
		return "X";
	if registers.Y == op:
		return "Y";
	if registers.Z == op:
		return "Z";
		
def getFreeRegister( registers ):
	if registers.A == None:
		return "A";
	if registers.B == None:
		return "B";
	if registers.C == None:
		return "C";
	if registers.I == None:
		return "I";
	if registers.J == None:
		return "J";
	if registers.X == None:
		return "X";
	if registers.Y == None:
		return "Y";
	if registers.Z == None:
		return "Z";
	return None;
	
def assignRegisters( pc ):
	global pseudocode;
	unorder = [ "@mul" , "@add" ];
	registers = ASTObject( "registry" , A= None , B= None , C= None , I= None , J= None , X= None , Y= None , Z= None , stack= [  ] );
	npc = [];
	for i in range( len( pc ) ):
		op = pc[i]
		npc.append( op );
		if op.args[0].type == "literal": # Fix Incorrecty ordered parameters
			if op.type in unorder:
				temp = op.args[1];
				op.args[1] = op.args[0];
				op.args[0] = temp;
			else:
				rec = op.args[1];
				if not op.haskey( "noret" ) and op.haskey("re"):
					rec = op.re;
				npc.append( ASTObject( "@set" , args= [ rec , op.args[0] ] ) );
				op.args[0] = rec;
		if not op.haskey( "noret" ) or op.noret == False: # Replace fake assignments with "set" operations
			if op.haskey("re") and op.re == op.args[0]:
				npc.append( ASTObject( "@set" , args= [ op.re , op.args[0] ] ) );
			elif op.haskey("re"):
				for j in range( len( pc ) - i ):
					oop = pc[i+j];
					for arg in oop.args:
						if arg.type == "var" and arg.name == op.re.name:
							arg._data = op.args[0]._data;
				op.re = op.args[0];
		op.noret = True;
	pc = [];
	for op in npc: # Scan for newly created stupidness
		pc.append( op );
		if op.type == "@set" and op.args[0].type == "var" and op.args[1].type == "var":
			if op.args[0].name == op.args[1].name:
				pc.pop();
	pseudocode = pc;
	return pc;
	
	
	
	
	
	
	
	