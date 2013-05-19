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

from IceLeaf import *

class ASTObject(object):
	"""An abstract syntax tree object, which has an identifying type,
	and then a dynamic set of variables. You can get the underlying
	dictionary with ._data
	"""
	def __init__( self , type , **data ):
		"""type  :  the type of the AST
		**data  :  the starting data for the AST
		"""
		self.type = type;
		self.data = data;
	
	def __getattribute__( self , name ):
		if name == "type":
			return object.__getattribute__( self , "type" );
		elif name == "_data":
			return object.__getattribute__( self , "data" );
		else:
			return object.__getattribute__( self , "data" )[name];
	
	def __setattribute__( self , name , value ):
		if name != "type" and name != "_data":
			object.__getattribute__( self , "data" )[name] = value;
		elif name == "_data":
			object.__setattribute__( self , "data" , value );
	
	def __str__( self ):
		return "ASTObject.%s%s"%(object.__getattribute__( self , "type" ),str( object.__getattribute__( self , "data" ) ) );