
import random

n=10
S = dict(enumerate(sorted(random.sample(range(-10,10), n))))

print 'algo 1:'
for i in xrange(n-3):
	a = S[i]
	j = i + 1
	k = n - 1
	while j < k:
		b = S[j]
		c = S[k]
		if a+b+c==0:
			print 'a=%i, b=%i, c=%i' % (a, b, c)
			break
		elif a+b+c>0:
			k -= 1
		else:
			j += 1


print '\nalgo 2:'
a = b = c = 0
for i in xrange(n-1):
	a = S[i]
	k = i + 1
	for j in xrange(k, n):
		b = S[j]
		c = 0 - a - b
		if c in S:
			print 'a=%i, b=%i, c=%i' % (a, b, c)
