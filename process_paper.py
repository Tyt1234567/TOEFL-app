
def if_key(text):
    key = False
    if text[:2] == '阅读' or text[:2] == '口语' or text[:2] == '综合' or text[:2] == '独立':
        key = True
    if text[0] == 'C' and text[1].isdigit():
        key = True
    if text[0] == 'L' and text[1].isdigit():
        key = True
    return key

def read_text(file):
    test = {}
    # 正则表达式匹配 '阅读'、'口语'、'综合'、'独立' 或者 [CL]开头的编号
    pattern = r'(阅读|口语|综合|独立|[CL]\d+)'

    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines = list(filter(lambda x: x != '\n', lines))
    lines = [line.strip() for line in lines]
    i = 0
    while i < len(lines):
        if if_key(lines[i]):
            loc = lines[i].index('：')
            key = lines[i][:loc]
            item = lines[i][loc + 1:]
        else:
            item+=lines[i]
            item += '\n'
            item += '\n'
        test[key] = item
        i+=1


    return test
