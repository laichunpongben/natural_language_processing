from functools import reduce

with open('input/stage1_text', 'r') as f:
    lines = f.readlines()
lines = lines[1:]
print(len(lines))

ids = [0, 7, 16, 37, 38, 41, 42]

word_groups = []
for id_ in ids:
    line = lines[id_]
    words = set(line.split(' '))
    word_groups.append(words)

print(len(word_groups))

result = sorted(list(reduce(lambda x, y: x.intersection(y), word_groups)))
print(result)
print(len(result))
