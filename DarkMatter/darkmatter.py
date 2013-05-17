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

def testrun():
	sourcefile = open( "testsource.dm" , "r" )
	source = sourcefile.read();
	sourcefile.close();


def main( argv ):
	print "The DarkMatter compiler for the DCPU16.\nWritten my Marco Aslak Persson.\n"
	testrun(); # a temporary testing function

if __name__ == "__main__":
	main( sys.argv );

