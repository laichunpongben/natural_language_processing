import re

patterns = [
    r"\(\w+\)",
    r"\(\d+\)",
    r"\( \d+\)",
    r"[ \t](?=[mdclxvi]{2,})m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})[ \t]",
    r"[ \t](?=[mdclxvi]{2,})m{0,4}(?:cm|cd|d?c{0,3})(?:xc|xl|l?x{0,3})(?:ix|iv|v?i{0,3})\-\d{0,2}[ \t]",
    r"[ \t]\-?(?=(?:\.|\d))(?:\d*|\d{1,3}(?:(?: |,)\d{3})*)(?:\.\d+)?[ \t]",
    r"http[^ \t]+",
    r"ftp[^ \t]+",
    r"www\.[^ \t]+",
    r"[ \t][\w\d_\.\+\-]+@[\w\d\-]+\.\d{2,3}[ \t]",
    r"[atcg]{10,}",
    r"\d{16,}",
    r"\d+%",
    r"\d+°c?[ \t]",
    r"#\d+",
    r"[ \t]\d+[\-–]\d+[ \t]",
    r"[\-–]/[\-–]",
    r"[ \t][\-–]",
    r"[\-–][ \t]",
    r"[ \t]/[ \t]",
    r"[ \t]\d+/\d+[ \t]",
    r"[ \t]\d\w[ \t]",
    # r"[ \t]\|[ \t]",
    r"[ \t](?:et al|et. al)",
    r"[ \t]levels?-\d",
    r"[\(\)\[\]\,\.\+\^\?\{\};:<>=#@%&“”‘’'–±≥×→↓⇓►©○• ′∗≈å∼~∷αβδμσγ„¢â«»≪‖†·¿ãÿ]",
    r"[ \t]\*+",
    r"[ \t]\d+[ \t]",
    r"[ \t]/\w[ \t]",
    r"[ \t]\w[ \t]",
    # r"\d+\|\|[^ \t]+[ \t]",
    r"[ \t][^ \t]+[\-_\/][^ \t]+[ \t]"
    r"[ \t](?:a|about|above|across|after|afterwards|again|against|all|almost|alone|along|already|also|although|always|am|among|amongst|amoungst|amount|an|and|another|any|anyhow|anyone|anything|anyway|anywhere|are|around|as|at|back|be|became|because|become|becomes|becoming|been|before|beforehand|behind|being|below|beside|besides|between|beyond|both|bottom|but|by|call|can|cannot|cant|co|con|could|couldnt|cry|de|describe|detail|did|do|does|doing|don|done|down|due|during|each|eg|eight|either|eleven|else|elsewhere|empty|enough|etc|even|ever|every|everyone|everything|everywhere|except|few|fifteen|fify|fill|find|fire|first|five|for|former|formerly|forty|found|four|from|front|full|further|get|give|go|had|has|hasnt|have|having|he|hence|her|here|hereafter|hereby|herein|hereupon|hers|herself|him|himself|his|how|however|hundred|i|ie|if|in|inc|indeed|interest|into|is|it|its|itself|just|keep|last|latter|latterly|least|less|ltd|made|many|may|me|meanwhile|might|mill|mine|more|moreover|most|mostly|"
    r"move|much|must|my|myself|name|namely|neither|never|nevertheless|next|nine|no|nobody|none|noone|nor|not|nothing|now|nowhere|of|off|often|on|once|one|only|onto|or|other|others|otherwise|our|ours|ourselves|out|over|own|part|per|perhaps|please|put|rather|re|same|see|seem|seemed|seeming|seems|serious|several|she|should|show|side|since|sincere|six|sixty|so|some|somehow|someone|something|sometime|sometimes|somewhere|still|such|system|take|ten|than|that|the|their|theirs|them|themselves|then|thence|there|thereafter|thereby|therefore|therein|thereupon|these|they|thickv|thin|third|this|those|though|three|through|throughout|thru|thus|to|together|too|top|toward|towards|twelve|twenty|two|un|under|until|up|upon|us|very|via|was|we|well|were|what|whatever|when|whence|whenever|where|whereafter|whereas|whereby|wherein|whereupon|wherever|whether|which|while|whither|who|whoever|whole|whom|whose|why|will|with|within|without|would|you|your|yours|yourself|yourselves|table|figures?|fig|"
    r"embedded image|image|°c)[ \t]",
]
patterns = [re.compile(p) for p in patterns]

text_path = 'input/stage2_test_text'

with open(text_path, 'r') as f:
    text = f.read()

text = text.lower()

gene_path = 'input/gene_variants'
with open(gene_path, 'r') as f1:
    genes = f1.readlines()
genes = [gene[:-1] for gene in genes]

# for gene in genes:
#     text = text.replace(" " + gene + " ", " ")

print(genes)
new_text = ''
documents = text.split("\n")
for i, doc in enumerate(documents):
    print(i)
    words = doc.split(" ")
    no_gene = list(set(words).intersection(set(genes)))
    no_gene.sort(key=lambda x: words.index(x))
    new_text += str(i) + '||' + ' '.join(no_gene) + ' \n'
# print(len(words))

# index_words = sorted([(index, word) for index, word in enumerate(words)], key=lambda x: x[1])
# words = sorted(list(zip(range(len(words)), words)), key=lambda x: x[1])
# print(len(index_words))
# words = sorted(words)

# for gene in genes:
#     idx = words.index(gene)
#     print(idx)
#     while index_words[idx][1] == gene:
#         index_words[idx] = (-1, None)
#         idx += 1
#
# index_words.sort(key=lambda x: -x[0])
# idx_none = index_words.index((-1, None))
# index_words = index_words[:idx_none]
# index_words = index_words[::-1]

# new_words = []
# for index, word in enumerate(words):
#     if word not in genes:
#         new_words.append(word)
        # print(index)
# words = [word for word in words if not word in genes]

# words = [word[1] for word in index_words]

print("Removed genes and variants")
# text = " ".join(words)
text = new_text
print(len(text))

for _ in range(2):
    for p in patterns:
        text = re.sub(p, " ", text)

text = re.sub(re.compile(r"[ \t]+"), " ", text)

output_path = 'input/stage2_text_gene'
with open(output_path, 'w') as f2:
    f2.write(text)
