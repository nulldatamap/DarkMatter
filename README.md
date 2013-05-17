DarkMatter
==========

DarkMatter is a dedicated programming language for the DCPU16.
It is a semi high-level langauge made to merge nicely with the low level nature of the DCPU16.
This project uses the [IceLeaf](https://github.com/thebreadcat/IceLeaf) library for lexing and parsing.
The offical DCPU16 forum thread can be found [here](http://0x10cforum.com/forum/m/4932880/viewthread/2742995-darkmatter-dedicated-programming-language-for-dcpu16-super-script-c)

Examples:
---------

Hello World:
```c
//This is a comment!
print("Hello World!\n")
```

100 beers and the wall:
```c
int beers = 100
while beers > 0
{
    print("" + beers + " on the wall.\n")
    print("You take 1 down, you pass it around and you've got ")
    beers--
}
print("no more beer on the wall!")
```

Functions:
```c

//syntax 1:
function int giveMeAnInt(int myInt)
{
    return myInt + 27 << 1
}
print("My int is: "  + giveMeAnInt(3))

//syntax 2:
int giveMeAnInt(int myInt)
{
    return myInt + 27 << 1
}
print("My int is " + giveMeAnInt(3))
```
