/* 

Below C Level: An Introduction to Computer Systems
Norm Matloff
University of California, Davis

"So, the machine doesn’t know whether we humans intend the bit string
we have stored in a 4-byte memory cell to be interpreted as an integer
or as a 4-element character string or whatever. To the machine, it is just a
bit string, 32 bits long.  The place the notion of types arises is at the
compiler/language level, not the machine level. The C/C++ language has its
notion of types, e.g. int and char, and the compiler produces machine code
accordingly. But that machine code itself does not recognize type. Again,
the machine cannot tell whether the contents of a given word are being thought
of by the programmer as an integer or as a 4-character string or whatever
else.  

For example, consider this code:

At first, you may believe that this code would not even compile successfully,
let alone run correctly. After all, the first argument to strncpy() is
supposed to be of type char *, yet we have the argument as type int
*. But the C compiler, say GCC, will indeed compile this code without error,
 and the machine code will indeed run correctly, placing “abcd” into Y.
 The machine won’t know about our argument type mismatch."
*/

#include <stdio.h>
#include <string.h>

int main()
{
    int y;  // local
    y = 10;
    strncpy(&y, "abcd", 4);
    printf("%d\n", y);  // 1684234849
}
