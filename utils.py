from resources import CodeableConcept, Coding, HumanName
from typing import Any, List
from datetime import datetime

def cc_str(codeableConcept_: CodeableConcept | None) -> str:
    """string representation of a codeable concept
    prefer text, otherwise first coding display, otherwise first coding code"""
    if not codeableConcept_ or not codeableConcept_.coding:
        return ""
    if codeableConcept_.text:
        return codeableConcept_.text
    if len(codeableConcept_.coding) == 0:
        return ""
    first_coding = codeableConcept_.coding[0]
    if first_coding.display:
        return first_coding.display
    if first_coding.code:
        return first_coding.code
    return ""

def dt_str(datetime_: str | None) -> str:
    """converts datetime string like 2015-05-18T18:12:58+00:00
    to format input type datetime-local can use as value"""
    if not datetime_:
        return ""
    dt = datetime.fromisoformat(datetime_)
    formatted = dt.strftime("%Y-%m-%dT%H:%M")
    return formatted

def hn_str(name: HumanName | None) -> str:
    """string representation of fhir humanName"""
    if not name:
        return ''
    if name.text:
        return name.text
    parts = []
    if name.prefix:
        parts.extend(name.prefix)
    if name.given:
        parts.extend(name.given)
    if name.family:
        parts.append(name.family)
    if name.suffix:
        parts.extend(name.suffix)
    ret = " ".join(parts).strip()
    if name.use and name.use.lower() != 'official':
        return f'({ret})'
    else:
        return ret
    
def hn_list_str(name_list: List[HumanName] | None) -> str:
    """string representation of list of fhir humanNames"""
    if not name_list:
        return ''
    return f"{'\n'.join(hn_str(name) for name in name_list)}"
