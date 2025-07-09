/*
FHIR codings have system, code, and display, but we only want to show one display to select
we could hook into the server side model validation to set system/code from display...
...which would be simpler in some ways, but would not show whole model in network request
so what setSystemAndCode does is set hidden inputs for code/system when selecting display
for example:
    <input id="maritalStatus_Display" name="maritalStatus.coding[0].display" list="marital-status-display-list" value="{patient.maritalStatus.coding[0].display if patient.maritalStatus else ''}" 
    onblur="setSystemAndCode(this, document.getElementById('maritalStatus_System'), document.getElementById('maritalStatus_Code'), document.getElementById('maritalStatus_Text'))">
    <datalist id="marital-status-display-list">
        {''.join(
            f'<option value="{item["display"]}" data-system="{item["system"]}" data-value="{item["code"]}"></option>'
            for item in (vs_patient_maritalStatus if patient else [])
        )}
    </datalist>
    <input type="hidden" id="maritalStatus_System" name="maritalStatus.coding[0].system" value="{patient.maritalStatus.coding[0].system if patient.maritalStatus else ''}">
    <input type="hidden" id="maritalStatus_Code" name="maritalStatus.coding[0].code" value="{patient.maritalStatus.coding[0].code if patient.maritalStatus else ''}">
    <input type="hidden" id="maritalStatus_Text" name="maritalStatus.text" value="{patient.maritalStatus.text if patient.maritalStatus else ''}">
or as select:

*/
function setSystemAndCode(input, elemSystem, elemCode, elemText) {
    let optionsList;
    if (input.tagName.toLowerCase() === 'select') {
        // If the input is a <select>, it has its own options list
        optionsList = input;
    } else if (input.tagName.toLowerCase() === 'input' ) {
        optionsList = document.getElementById(input.getAttribute('list'));
        // normal input should have a datalist that list attr points to
    } else {
        console.error('setSystemAndValue: Input must be a <select> or an <input> with a datalist.');
        return;
    }

    const val = input.value.trim().toLowerCase();
    //check for empty because "" included in every display value
    //but empty means clear, not any display value
    if (!val) {
        clearSystemAndCode(elemSystem, elemCode, elemText);
        return;
    }
    //try to find display value that includes our input and set system/value based on that
    const opts = optionsList.querySelectorAll('option');
    if (!opts || opts.length === 0) {
        //no options in datalist, so clear values
        clearSystemAndCode(elemSystem, elemCode, elemText);
        return;
    }
    for (let opt of opts) {
        if (opt.value.toLowerCase().includes(val)) {
            input.value = opt.value;
            elemSystem.value = opt.dataset.system;
            elemCode.value = opt.dataset.code;
            if(elemText) {
                elemText.value = opt.value;
            }
            //might not have text because a coding is just system/value/display
            //codeableconcept also has text but you can use this with just a coding
            return;
        }
    }
    clearSystemAndCode(elemSystem, elemCode, elemText);
}

function clearSystemAndCode(elemSystem, elemCode, elemText) {
    elemSystem.value = '';
    elemCode.value = '';
    if(elemText) {
        elemText.value = '';
    }
}