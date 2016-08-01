#include <stdio.h>

/*
The point also applies to local variables. We can actually access a 
local variable in one function from code in another function. The 
following example demonstrates that (make sure to review Section 7.8.8 
before reading the example):
*/

void g()
{ 
    int i,*p;
    p = &i;
    p = p + 1; /* p now points to main()’s EBP */
    p = *p; /* p now equals main()’s EBP value */
    p = p - 1; /* p now points to main()’s x */
    *p = 29; /* changes x to 29 */
}

/* I get a segfault when I run this */
main()
{ 
    int x = 5; /* x is local to main() */
    g();
    printf("%d\n",x); /* prints out 29 */
}

