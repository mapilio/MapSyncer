function updateJson(event) {
    event.preventDefault();

    var formData = new FormData(event.target);

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


document.addEventListener("DOMContentLoaded", function() {
    const allProgressBars = document.querySelectorAll('.progress-bar');
    allProgressBars.forEach(function(progressBar) {
        progressBar.parentElement.style.visibility = 'hidden';
    });
});

function downloadSequence(sequenceId, button, to_path) {
    button.classList.remove('btn-outline-secondary');
    button.classList.add('disabled', 'btn-warning');
    button.textContent = 'Downloading';

    const progressBarContainer = document.getElementById('progressBarContainer_' + sequenceId);
    const progressBar = document.getElementById('progressBar_' + sequenceId);
    const progressCount = document.getElementById('progressCount_' + sequenceId);

    progressBar.parentElement.style.visibility = 'visible';
    progressBarContainer.classList.add('my-2');

    let downloadFinished = false;

    fetch('/download-sequence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'to_path': to_path,
            'sequence_id': sequenceId
        })
    }).then(response => {
        if (response.ok) {
            button.classList.remove('disabled', 'btn-warning');
            button.classList.add('btn-success', 'disabled');
            button.textContent = 'Downloaded';
            alert('Sequence ' + sequenceId + ' downloaded successfully!');
            setTimeout(function () {
                document.getElementById('disableUpload_' + sequenceId).classList.remove('disabled');
                progressBar.parentElement.style.visibility = 'hidden';
                progressBarContainer.classList.remove('my-2');
                downloadFinished = true;
            }, 2000);
        } else {
            button.classList.remove('disabled', 'btn-warning');
            button.classList.add('btn-danger');
            button.textContent = 'Failed, Try again.';
            alert('Failed to download sequence ' + sequenceId + '. You can try again.');
        }
    }).catch(error => {
        console.error('Error during sequence download:', error);
        button.classList.remove('disabled', 'btn-warning');
        button.classList.add('btn-warning');
        button.textContent = 'Error, Try again.';
        alert('An error occurred during sequence ' + sequenceId + ' download. You can try again.');
    });


    function fetchProgress() {
        if (downloadFinished) {
            clearInterval(interval);
            return;
        }

        fetch('/download-progress-bar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({
                    'sequence_id': sequenceId
                })
            }).then(response => {
                if (response.ok) {
                    return response.json();
                }
            }).then(data => {
                const countPhotos = data.photos;
                const countProcess = data.progress;

                progressBar.setAttribute('aria-valuenow', countProcess);
                const widthPercentage = (countProcess / countPhotos) * 100;
                progressBar.style.width = widthPercentage + '%';

                progressBar.textContent = widthPercentage.toFixed(2) + '%';

                progressBar.setAttribute('aria-valuemax', countPhotos);
            }).catch(error => {
                console.error('Error fetching download progress:', error);
            });
        }

    const interval = setInterval(fetchProgress, 2000);
}



function downloadAll() {
    var downloadButtons = document.querySelectorAll('[id^="downloadButton"]');
    downloadButtons.forEach(function(button) {
        if (!button.classList.contains('disabled')) {
            button.click();
        }
    });
}


function uploadSequence(sequenceId, button, to_path) {
    button.classList.remove('btn-outline-secondary');
    button.classList.add('disabled', 'btn-warning');
    button.textContent = 'Uploading';

    fetch('/upload-sequence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'to_path': to_path,
            'sequence_id': sequenceId
        })
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data.status === 'success') {
            button.classList.remove('disabled','btn-warning');
            button.classList.add('btn-success', 'disabled');
            button.textContent = 'Uploaded';
            alert('Sequence ' + sequenceId + ' uploaded successfully!');
        } else {
            button.classList.remove('disabled', 'btn-warning');
            button.classList.add('btn-danger');
            button.textContent = 'Failed, Try again.';
            alert('Sequence ' + sequenceId + ' could not be uploaded. ' + data.message);
        }
    }).catch(error => {
        console.error('Error during sequence upload:', error);
        button.classList.remove('disabled', 'btn-warning');
        button.classList.add('btn-warning');
        button.textContent = 'Error, Try again.';
        alert('An error occurred during sequence ' + sequenceId + ' upload. You can try again.');
    });
}

function downloadRange(button) {
    button.classList.add('disabled', 'btn-warning');
    button.textContent = 'Downloading';
    var startNumberID = document.getElementById('startNumberID').value;
    var endNumberID = document.getElementById('endNumberID').value;

    if (startNumberID === "" || endNumberID === "") {
        button.classList.remove('disabled', 'btn-warning');
        button.textContent = 'Download range';
        alert("Please enter start and end sequence Number IDs.");
        return;
    }

    var startNumberIDNum = parseInt(startNumberID);
    var endNumberIDNum = parseInt(endNumberID);

    if (startNumberIDNum > endNumberIDNum) {
        var temp = startNumberID;
        startNumberID = endNumberID;
        endNumberID = temp;
    }

    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        var numberID = card.querySelector('.card-text b:nth-child(1)').textContent.trim().split(':')[1].trim();
        if (parseInt(numberID) >= parseInt(startNumberID) && parseInt(numberID) <= parseInt(endNumberID)) {
            var downloadButton = card.querySelector('.btn-m');
            if (!downloadButton.classList.contains('disabled')) {
                downloadButton.click();
            }
        }
    });

    button.classList.remove('disabled', 'btn-warning');
    button.textContent = 'Download range';
}