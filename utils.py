from resources import CodeableConcept, Coding

def cc_str(cc: CodeableConcept) -> str:
    """string representation of a codeable concept
    prefer first coding display, otherwise first coding code, otherwise text"""
    if not cc or not cc.coding or len(cc.coding) == 0:
        return ""
    first_coding = cc.coding[0]
    if first_coding.display:
        return first_coding.display
    if first_coding.code:
        return first_coding.code
    if cc.text:
        return cc.text
    return ""