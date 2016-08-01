

/* 
Below C Level: An Introduction to Computer Systems
Norm Matloff
University of California, Davis

"When we say that the hardware doesn’t know types, that includes
array types. Consider the following program:
*/

#include <stdio.h>

main()
{
    int X[5],Y[20],I;

    X[0] = 12;
    
    // read in I = 20 
    // (won't compile with hard-coded index)
    scanf("%d",&I); 
    
    Y[I] = 15;
    printf("X[0] = %d\n",X[0]); // prints out 15!
}



/* 
"There appears to be a glaring problem with Y here. We assign 15
to Y[20], even though to us humans there is no such thing as Y[20];
the last element of Y is Y[19]. Yet the program will indeed run 
without any error message, and 15 will be printed out.

To understand why, keep in mind that at the machine level there is really
no such thing as an array. Y is just a name for the first word of the 20
words we humans think of as comprising one package here. When we write the
C/C++ expression Y[I], the compiler merely translates that to machine code
which accesses “the location I ints after Y.”

This should make sense to you since another way to write Y[I] is ∗(Y+I).
So, there is nothing syntactically wrong with the expression Y[20]. Now,
where is “Y[20]”? C/C++ rules require that local variables be stored
in reverse order,11 i.e. Y first and then X. So, X[0] will follow 
immediately after Y[19]. Thus “Y[20]” is really X[0], and thus X[0] will
become equal to 15!"
*/
