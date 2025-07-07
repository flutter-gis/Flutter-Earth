import re

input_file = 'frontend/generated_themes.js'

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to find single-quoted string values with an apostrophe inside
pattern = re.compile(r"(:\s*)'([^'\n]*'[^'\n]*)'", re.MULTILINE)

def replacer(match):
    prefix = match.group(1)
    value = match.group(2)
    # Only replace if there is an apostrophe in the value
    if "'" in value:
        return f'{prefix}"{value}"'
    else:
        return match.group(0)

fixed_content = pattern.sub(replacer, content)

with open(input_file, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print('All problematic single-quoted strings with apostrophes have been fixed.') 