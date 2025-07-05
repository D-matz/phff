from typing import Dict, Any
from pydantic import model_validator
from fhir.resources.R4B.allergyintolerance import AllergyIntolerance as FhirAllergyIntolerance
from fhir.resources.R4B.codeableconcept import CodeableConcept

def remove_empty_strings_recursive(obj):
    if isinstance(obj, dict):
        return {
            k: v
            for k, v in (
                (k, remove_empty_strings_recursive(v))
                for k, v in obj.items()
            )
            if v != "" and v != [] and v != {}
        }
    elif isinstance(obj, list):
        cleaned = [remove_empty_strings_recursive(item) for item in obj]
        # Remove empty strings, empty dicts, and empty lists from lists
        return [item for item in cleaned if item != "" and item != [] and item != {}]
    else:
        return obj

class AllergyIntolerance(FhirAllergyIntolerance):
    @model_validator(mode="before")
    @classmethod
    def remove_empty_strings(cls, values: Dict[str, Any]):
        """Treat empty strings as not having the field
        so if you have an input, select, date, etc with "" in form
        that field will be removed from resource"""
        return remove_empty_strings_recursive(values)

    valueset_code: list[dict[str, str]] = [
        { "system": "http://snomed.info/sct", "code": "91930004", "display": "Allergy to eggs" },
        { "system": "http://snomed.info/sct", "code": "91932001", "display": "Allergy to peanuts" },
        { "system": "http://snomed.info/sct", "code": "91936005", "display": "Allergy to latex" },
        { "system": "http://snomed.info/sct", "code": "300916003", "display": "Allergy to penicillin" },
        { "system": "http://snomed.info/sct", "code": "300913006", "display": "Allergy to sulfonamide" },
        { "system": "http://snomed.info/sct", "code": "26743006", "display": "House dust mite allergy" },
        { "system": "http://snomed.info/sct", "code": "441952005", "display": "Allergy to tree pollen" },
        { "system": "http://snomed.info/sct", "code": "414285001", "display": "Allergy to grass pollen" },
        { "system": "http://snomed.info/sct", "code": "419474003", "display": "Allergy to cat dander" },
        { "system": "http://snomed.info/sct", "code": "294259002", "display": "Allergy to penicillin V" },
        { "system": "http://snomed.info/sct", "code": "420246004", "display": "Allergy to ragweed" },
        { "system": "http://snomed.info/sct", "code": "300914000", "display": "Allergy to cephalosporin antibiotic" },
        { "system": "http://snomed.info/sct", "code": "277132007", "display": "Allergy to latex (finding)" },
        { "system": "http://snomed.info/sct", "code": "227493005", "display": "Cashew nut allergy" },
        { "system": "http://snomed.info/sct", "code": "300915001", "display": "Allergy to aminopenicillin antibiotic" },
        { "system": "http://snomed.info/sct", "code": "300918004", "display": "Allergy to penicillin G" },
        { "system": "http://snomed.info/sct", "code": "294163004", "display": "Allergy to codeine" },
        { "system": "http://snomed.info/sct", "code": "235719002", "display": "Allergy to iodine" },
        { "system": "http://snomed.info/sct", "code": "235719002", "display": "Allergy to iodine" },
        { "system": "http://snomed.info/sct", "code": "300917000", "display": "Allergy to cephalothin" },
        { "system": "http://snomed.info/sct", "code": "300919007", "display": "Allergy to penicillamine" },
        { "system": "http://snomed.info/sct", "code": "300921000", "display": "Allergy to penicillin antibiotic" }
    ]
