function initDropZone(fileInput, container) {
    if(typeof container === 'string')
    {
        container = document.getElementById(container);
    }
    if(!container)
    {
        console.error("drop-file.js: initDropZone called without a main container to attach overlay to.\
            initDropZone attaches to container elt rather than body so that htmx replacing content \
            will stop initDropZone from running once the page has been replaced");   
    }


    if (typeof fileInput === 'string') {
        fileInput = document.getElementById(fileInput);
    }
    if(!fileInput)
    {
        console.error("drop-file.js: initDropZone called without a fileInput element to drop file into");
    }

    const overlay = document.createElement('div');
    overlay.innerHTML = '<div style="padding: 20px; border-radius: 8px; text-align: center; font-size: 25px; border: 2px dashed;">Drop file here</div>';
    overlay.classList.add('color-primary');
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; opacity: 50%; display: none; align-items: center; justify-content: center; z-index: 1000; pointer-events: none;';
    overlay.classList.add('color-primary');
    document.body.appendChild(overlay);
    let dragCount = 0;

    container.addEventListener('dragenter', e => {
        e.preventDefault();
        if (e.dataTransfer.types.includes('Files')) {
            dragCount++;
            overlay.style.display = 'flex';
        }
    });

    container.addEventListener('dragleave', e => {
        e.preventDefault();
        dragCount--;
        if (dragCount <= 0) overlay.style.display = 'none';
    });

    container.addEventListener('dragover', e => e.preventDefault());

    container.addEventListener('drop', e => {
        e.preventDefault();
        dragCount = 0;
        overlay.style.display = 'none';
        
        if (e.dataTransfer.files.length > 0) {
            // Create new FileList with just the first file
            const dt = new DataTransfer();
            dt.items.add(e.dataTransfer.files[0]);
            fileInput.files = dt.files;
            fileInput.dispatchEvent(new Event('change'));
            //console.log("drop-file dispatchEvent"); 
        }
    });
}