import sys

if len(sys.argv) <= 1:
    sys.exit(0)

filename = sys.argv[1]

total = 0
num = 0
for line in open(filename, "r"):
    total += float(line)
    num += 1

print "Average:", (total*1.0)/num
