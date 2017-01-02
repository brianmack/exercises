
# Found this G. Strang gem while reviewing linear algebra fundamentals.
# Let's do a novel Fibonacci function.  We store a current state in a 2x2 
# matrix with k+1, k, and k-1.  We also have a transformer matrix, which
# we apply k times.  The state matrix remains unchanged between calls,
# so we don't have to start at the bottom each time.  It goes back down,
# too, by calling the inverse transormation.  Hopefully, our calls to this
# function have values 'nearby' the previous!

# I check it against the traditional memoized fibonaaci function at each
# step.

# the 'STATE' matrix 
# | k+1, k   |
# | k,   k-1 |

FIB = [1 1 ; 1 0]
STATE = [1 1 ; 1 0]
K = 1 # represents values in 1,0, 0,1 
function fib(n)
    
    global FIB
    global STATE
    global K
    
    while n < K
        STATE = STATE * inv(FIB)
        K -= 1
    end
    while n > K
	    STATE = FIB * STATE 
    	K += 1
    end
    return STATE[1, 2]
end


# the traditional way
CACHE = Dict(0=>0, 1=>1)
function testfib(n)
    
    global CACHE

    if haskey(CACHE, n)
        return CACHE[n]
    end
    return testfib(n - 1) + testfib(n - 2)
end


print("testing n = 10;  ")
value = fib(10)
@assert value == testfib(10)
println("passed.")

print("testing n = 4;  ")
value = fib(4)
@assert value == testfib(4)
println("passed.")

print("testing n = 20;  ")
value = fib(20)
@assert value == testfib(20)
println("passed.")


println("all done :)")

