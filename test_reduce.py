def separate(arr, x):
  if x - arr[-1][-1] < 4:
    arr[-1].append(x)
  else:
    arr.append([x])
  return arr

a = [1,2,3,7,8,10,11,12,18,19,20,23,30]
b = reduce(separate, a[1:], [a[0:1]])

