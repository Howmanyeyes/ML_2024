n, q = (int(x) for x in input().split(" "))
saturation = [int(x) for x in input().split(" ")]

for i in range(q):
    l, r = (int(x) for x in input().split(" "))
    avaliable = saturation[l-1:r]
    min_val = min(avaliable)

    print(min_val - l)
 # нецелые числа?