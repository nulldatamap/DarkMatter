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

# dmlex.py the lexing functions of the compiler

from IceLeaf import *

# ================= A little token brainstorm =======================
# FOR DO WHILE TRUE FALSE IF ELSE SWITCH CASE BREAK CONTINUE STRING
# HEX OCT INT IDENT OBRKT CBRKT OPAREN CPAREN OBRCE CBRCE OANG CANG
# EQL PLUS MINUS AT MULT DIV AND OR XOR MOD COLON QUEST EXCL TILD DOT
# COMMA SEMICOLON
# ===================================================================

# State functions:

def stateBroken( lexer , statename ):
	"""This state function will be called when a open/close pair failed
	but the open part is found( A.k.a. a string or block comment that is not closed )
	"""
	if statename == "BROKEN_COMMENT":
		raise StateError( "broken comment" , "no block comment ending was found!" , lexer.pos , lexer.line );
	elif statename == "BROKEN_STRING": # This is also the name of a good track.
		raise StateError( "broken string" , "no string ending was found!" , lexer.pos , lexer.line );

# Keywords:

keywords = [ "for" , "do" , "while" , "true" , "false" , "if" , "else" , "switch" , "case" , "break" , "continue" , "struct" , "repeat" ];

# Lexing rules:

lNewline = LexerRule( "NEWLINE" , "\n" , 0 , True );
lIgnore = LexerRule( "IGNORE" , "[\r \t]" );
lComment = LexerRule( "COMMENT" , r"(//[^\n]*)|(/\*(.|\n)*\*/)" , 0 , True ); # Comments are still lexed, and are saved in channel 0 as hidden tokens
sBrokenComment = LexerRule( "BROKEN_COMMENT" , r"/\*" , stateBroken ); # If the valid comment check didn't work, but the 'not closed' comment check did, raise an error
lString = LexerRule( "STRING" , '("((\\\\")|[^"])*[^\\\\]")|\'((\\\\\')|[^\'])*[^\\\\]\'' ); # Both single and double quote strings
lEString = LexerRule( "STRING" , '("")|(\'\')' );
lHex = LexerRule( "HEX" , "0x[a-fA-F0-9]+" );
lOct = LexerRule( "OCT" , "0[0-8]+" );
lInt = LexerRule( "INT" , "-?[0-9]+" );
lIdent = LexerRule( "IDENT" , "[a-zA-Z_][a-zA-Z0-9_]*" );
# combined operators
# == <> != ~= += -= *= /= %= &= |= ^= <= >= && || << >> >>>
lEql = LexerRule( "EQL" , "==" );
lNotEql = LexerRule( "NOTEQL" , "(<>)|(!=)" );
lNotAssign = LexerRule( "NOTASSIGN" , "~=" );
lAddAssign = LexerRule( "ADDASSIGN" , "\\+=" );
lSubAssign = LexerRule( "SUBASSIGN" , "-=" );
lMulAssign = LexerRule( "MULASSIGN" , "\\*=" );
lDivAssign = LexerRule( "DIVASSIGN" , "/=" );
lModAssign = LexerRule( "MODASSIGN" , "%=" );
lAndAssign = LexerRule( "ANDASSIGN" , "&=" );
lOrAssign = LexerRule( "ORASSIGN" , "\\|=" );
lXorAssign = LexerRule( "XORASSIGN" , "\\^=" );
lLessEql = LexerRule( "LESSEQL" , "<=" );
lGreatEql = LexerRule( "GREATEQL" , ">=" );
lLogicAnd = LexerRule( "LOGICAND" , "&&" );
lLogicOr = LexerRule( "LOGICOR" , "\\|\\|" );
lLeftShift = LexerRule( "LSHIFT" , "<<" );
lRightShift = LexerRule( "RSHIFT" , ">>" );
lSignedShift = LexerRule( "SSHIFT" , ">>>" );
lIncrement = LexerRule( "INC" , "\\+\\+" );
lDecrement = LexerRule( "DEC" , "--" );
# single operators
# [ ] ( ) { } < > = + - @ * / & | ^ % : ? ! ~ . , ;
lOBrkt = LexerRule( "OBRKT" , "\\[" );
lCBrkt = LexerRule( "CBRKT" , "\\]" );
lOParen = LexerRule( "OPAREN" , "\\(" );
lCParen = LexerRule( "CPAREN" , "\\)" );
lOBrce = LexerRule( "OBRCE" , "{" );
lCBrce = LexerRule( "CBRCE" , "}" );
lOAngl = LexerRule( "OANGL" , "<" );
lCAngl = LexerRule( "CANGL" , ">" );
lAssign = LexerRule( "ASSIGN" , "=" );
lAdd = LexerRule( "ADD" , "\\+" );
lSub = LexerRule( "SUB" , "-" );
lAt = LexerRule( "AT" , "@" );
lMul = LexerRule( "MUL" , "\\*" );
lDiv = LexerRule( "DIV" , "/" );
lAnd = LexerRule( "AND" , "&" );
lOr = LexerRule( "OR" , "\\|" );
lXor = LexerRule( "XOR" , "\\^" );
lMod = LexerRule( "MOD" , "%" );
lColon = LexerRule( "COLON" , ":" );
lQuest = LexerRule( "QUEST" , "\\?" );
lExcla = LexerRule( "EXCLA" , "!" );
lTilde = LexerRule( "TILDE" , "~" );
lDot = LexerRule( "DOT" , "\\." );
lComma = LexerRule( "COMMA" , "," );
lSemiColon = LexerRule( "SEMICOLON" , ";" );

rules = [ lNewline, lIgnore, lComment, sBrokenComment, lString , lEString , lHex, lOct,
	lInt, lIdent, lEql, lNotEql, lNotAssign, lAddAssign, lSubAssign,
	lMulAssign, lDivAssign, lModAssign, lAndAssign, lOrAssign, lXorAssign,
	lLessEql, lGreatEql, lLogicAnd, lLogicOr , lLeftShift , lRightShift ,
	lSignedShift , lIncrement , lDecrement , lOBrkt, lCBrkt, lOParen, lCParen,
	lOBrce, lCBrce, lOAngl, lCAngl, lAssign, lAdd, lSub, lAt, lMul, lDiv, lAnd,
	lOr, lXor, lMod, lColon, lQuest, lExcla, lTilde, lDot, lComma, lSemiColon ]

# Lexing

def applyKeywords( tokens ):
	"""Takes a list of tokens, checks if the IDENT tokens match a keywords
	and turn it into a keyword token.
	"""
	for i in range( len( tokens ) ):
		t = tokens[i];
		if t.type == "IDENT":
			if keywords.count( t.data ) != 0:
				t.type = t.data.upper();
	return tokens;

class DMLexer(Lexer):
	def __init__( self ):
		Lexer.__init__( self , *rules );
	def lex( self , tokens ):
		return applyKeywords( Lexer.lex( self , tokens ) );
