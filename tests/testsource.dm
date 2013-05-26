//This is a comment!
print("Hello World!\n")

struct predef;

const predef var = predef{  };

typedef &char string;
typedef &string strings;

struct Player
{
	int health;
	&player self;
	char name[100];
}
//label:
&int[] array = [1,];

player = Player{ health = 10 , name= "John"+0 }

char top(  )
{
	2 + 3 + 1;
}

int beers = 100
while beers > 0
{
    print("" + beers + " on the wall.\n")
    print("You take 1 down, you pass it around and you've got ")
    beers--
}
print("no more beer on the wall!")

//syntax 2:
int giveMeAnInt(int myInt)
{
    return myInt + 27 << 1
}
print("My int is " + giveMeAnInt(3))
print("" + beers + " on the wall.\n")
print("You take 1 down, you pass it around and you've got ")
beers--
bob = @jorge;
if 0==1
{
	print( "Hello world!" );
}else if ( n != p || x >= y + 3 )
{
	print "I have no idea about this one"
}else
{
	print("This will be printed")
}
for( int i = 0; i < 10; i++ )
{
	print("meh");
}
for( int i = 0; i < 10; i++ ) n = i*3;
while true i++; // This only works because `true` is a keyword, if you used a variable you would need to have some sort of serpation, else the parser would think you were trying to declare a variable.
do i++ while true;
repeat n*10 with int i
{
	print( "I'm repeating myself!" )
	break;
}
switch ( x )
{
	case 0x01:
		c = a + b;
		break;
	case 0x02:
		c = a * b;
		break;
	default:
		print("ERROR");
}
& &int lel;

void function( int v );

void functiom( int v )
{
	print( "I'm the definition!" )
}


