import re
content = open('translations/ar/LC_MESSAGES/messages.po', encoding='utf-8').read()
pairs = re.findall(r'msgid \"(.+)\"\nmsgstr \"(.+)\"', content)
placeholders = [p[0] for p in pairs if p[0] == p[1]]
for p in placeholders:
    print(p)
