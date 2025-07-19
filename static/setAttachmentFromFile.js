/*
point is to turn file input into FHIR attachment data structure
when user adds a file, set hidden inputs data and contentType
also, if given form as argument, trigger post to submit form
*/
function setAttachmentFromFile(fileInput, contentTypeInput, dataInput, form = null) {  
  //console.log("setAttachmentFromFile"); 
  const file = fileInput.files[0];   
  if (!file) return;    

  const reader = new FileReader();
  
  reader.onload = e => {
    const base64Data = e.target.result.split(',')[1];
    contentTypeInput.value = file.type;   
    dataInput.value = base64Data;   
    
    if(form != null) {     
      htmx.trigger(form, 'submit');      
    }
  };
  
  reader.onerror = error => {
    console.error('Error reading file:', error);
  };
  
  reader.readAsDataURL(file);
}