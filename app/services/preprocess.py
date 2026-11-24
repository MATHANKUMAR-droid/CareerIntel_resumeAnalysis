import re,unicodedata

def clean_text(text:str)->str:
    text=unicodedata.normalize('NFKC',text).replace('\u2022','-').replace('\u00ad','')
    text=re.sub(r'(?<=\w)-\s*\n\s*(?=\w)','',text)
    lines=[re.sub(r'\s+',' ',x).strip() for x in text.splitlines()]
    lines=[x for x in lines if x and not re.fullmatch(r'page\s+\d+(\s+of\s+\d+)?',x,re.I)]
    return '\n'.join(lines)
