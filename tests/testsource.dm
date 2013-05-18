//This is a comment!
print("Hello World!\n")

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