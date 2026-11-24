from datetime import date
import re

def month_index(s):
    if not s:return None
    if s.lower()=='present':
        d=date.today();return d.year*12+d.month
    m=re.search(r'(\d{4})-(\d{2})',s)
    return int(m.group(1))*12+int(m.group(2)) if m else None

def union_months(ranges):
    vals=sorted((a,b) for a,b in ranges if a is not None and b is not None and b>a)
    if not vals:return 0
    total=0; start,end=vals[0]
    for a,b in vals[1:]:
        if a<=end:end=max(end,b)
        else:total+=end-start;start,end=a,b
    return total+end-start

def calculate_totals(experiences, skills):
    ranges=[]; leadership=[]; per={}
    for e in experiences:
        a=month_index(e.start_date);b=month_index(e.end_date)
        if a and b:ranges.append((a,b))
        if e.is_leadership and a and b:leadership.append((a,b))
        for skill in set(e.technologies):
            if a and b:per.setdefault(skill,[]).append((a,b))
    years=lambda r:round(union_months(r)/12,2)
    return {'total_experience_years':years(ranges),'leadership_years':years(leadership),'per_skill_years':{k:years(v) for k,v in per.items()}}
