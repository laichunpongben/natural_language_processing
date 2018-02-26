with open('input/test_text', 'r') as f:
    lines = f.readlines()

with open('input/test_text_2', 'w') as f2:
    for line in lines:
        if '||' in line:
            parts = line.split('||')
            head = str(int(parts[0]) + 3321)
            print(head)
            parts = [head] + parts[1:]
            line = '||'.join(parts)
        f2.write(line)
