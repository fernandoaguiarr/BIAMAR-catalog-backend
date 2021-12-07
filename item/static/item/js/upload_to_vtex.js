const saveButton = [...document.getElementsByName('_save')][0];
const headerCheckbox = document.getElementById('action-toggle');
const checkboxes =[...document.getElementsByName('_selected_sku')]
const actionRadioButton = [...document.getElementsByName('_selected_action')];

bindEventListeners();

function bindEventListeners(){
    [...checkboxes, ...actionRadioButton].forEach(element => element.addEventListener('click', onCheckboxChecked, false));
    headerCheckbox.addEventListener('click',onToggleCheckBoxes, false);
}

function checkSubmitButtonState(toggleAll=false){
    let firstCheck = true;
    let allowDelete = false;
    let disableButton = true;
    let exportedSkus = [...document.getElementsByName("_selected_sku")][0].value;

    for (let i in checkboxes){
        if (checkboxes[i].checked && actionRadioButton[1].checked){
            if (firstCheck){
                firstCheck = false;
                allowDelete = allowDelete || (exportedSkus.includes(checkboxes[i].value));
            } else {
                allowDelete = allowDelete && (exportedSkus.includes(checkboxes[i].value));
            }
        }
        disableButton = disableButton && ((!checkboxes[i].checked)? true:false);
     }

    if (actionRadioButton[1].checked){
        saveButton.disabled=disableButton  || !allowDelete;
    }
    else if (toggleAll) saveButton.disabled=!headerCheckbox.checked;
    else saveButton.disabled=disableButton;

}

function onToggleCheckBoxes(){
    for (let i in checkboxes ) checkboxes[i].checked = headerCheckbox.checked;
    checkSubmitButtonState();
}

function onCheckboxChecked(element){
    checkSubmitButtonState();
    if (!element.checked && headerCheckbox.checked) headerCheckbox.checked = !headerCheckbox.checked;
}

function onCloseWindow(){
    window.close();
    return false;
}

