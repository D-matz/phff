from typing import Dict, Any
from pydantic import model_validator
from fhir.resources.R4B.patient import Patient as FhirPatient
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

class Patient(FhirPatient):
    @model_validator(mode="before")
    @classmethod
    def remove_empty_strings(cls, values: Dict[str, Any]):
        """Treat empty strings as not having the field
        so if you have an input, select, date, etc with "" in form
        that field will be removed from resource"""
        return remove_empty_strings_recursive(values)

    valueset_maritalStatus: list[dict[str, str]] = [
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "A", "display": "Annulled" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "D", "display": "Divorced" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "I", "display": "Interlocutory" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "L", "display": "Legally Separated" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "M", "display": "Married" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "C", "display": "Common Law" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "P", "display": "Polygamous" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "T", "display": "Domestic partner" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "U", "display": "Unmarried" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "S", "display": "Never Married" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-MaritalStatus", "code": "W", "display": "Widowed" },
        { "system": "http://terminology.hl7.org/CodeSystem/v3-NullFlavor", "code": "UNK", "display": "Unknown" }
    ]