function updateJson(event) {
    event.preventDefault();
    var formData = new FormData(event.target);
    var seqId = formData.get('seq_id').trim();
    var progress = formData.get('key');
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/sequence-edit', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var alertContainer = document.getElementById('alertContainer');
            var alertMessage = document.createElement('div');
            alertMessage.classList.add('alert');
            if (xhr.status === 200) {
                alertMessage.classList.add('alert-success');
                alertMessage.textContent = 'Success: ' + xhr.responseText;
                if (progress === "download_success") {
                    var value = formData.get('new_value') === "true";
                    storeData(seqId, false, false, value, false)
                } else if (progress === "upload_success") {
                    var value = formData.get('new_value') === "true";
                    storeData(seqId, false, false, false, value)
                }
            } else {
                alertMessage.classList.add('alert-danger');
                alertMessage.textContent = 'Error: ' + xhr.responseText;
            }
            alertContainer.innerHTML = '';
            alertContainer.appendChild(alertMessage);
        }
    };
    xhr.send(formData);
}