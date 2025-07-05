function setValueAndSystem(input, elemSystem, elemValue, elemText) {
    const optionsList = document.getElementById(input.getAttribute('list'));
    //should not be null because input should have a datalist that list attr points to
    const val = input.value.trim().toLowerCase();
    //check for empty because "" included in every display value
    //but empty probably means clear instead of first display value
    if (!val) {
        input.value = '';
        elemSystem.value = '';
        elemValue.value = '';
        elemText.value = '';
        return;
    }
    //try to find display value that includes our input and set system/value based on that
    const opts = optionsList.querySelectorAll('option');
    for (let opt of opts) {
        if (opt.value.toLowerCase().includes(val)) {
            input.value = opt.value;
            elemSystem.value = opt.dataset.system;
            elemValue.value = opt.dataset.value;
            elemText.value = opt.value;
            return;
        }
    }
    input.value = '';
    elemSystem.value = '';
    elemValue.value = '';
    elemText.value = '';
}
