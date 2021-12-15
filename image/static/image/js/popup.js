function getParentElement(el){
    if(el.id && el.id.includes('group_has_photo')) return el;
    return getParentElement(el.parentElement);
}

function popItUp(el) {
    let parent = getParentElement(el);

    if (parent){
        color = [...parent.getElementsByClassName('field-color')][0];
        color = [...color.getElementsByClassName('related-widget-wrapper')][0];
        color = [...color.getElementsByTagName('select')][0]

        photo = [...parent.getElementsByClassName('field-file')][0];
        photo = [...photo.getElementsByClassName('file-upload')][0];

        if (photo && color){
            color = color.value;
            photo = [...photo.getElementsByTagName('a')][0].href;
            photo = photo.split('/').at(-1);
            photo = photo.split('.')[0];


            newWindow=window.open(`vtex/?color=${color}&file=${photo}`,'{{title}}','height=710,width=950');
            if (window.focus) {newWindow.focus()}
        }
    }
    return false;
}