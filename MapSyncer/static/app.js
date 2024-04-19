const progressBarVisibility = 'hidden';
const buttonDisabledClass = 'disabled';
const buttonWarningClass = 'btn-warning';
const buttonSuccessClass = 'btn-success';
const buttonDangerClass = 'btn-danger';
const buttonOutlineSecondaryClass = 'btn-outline-secondary'

function handleButtonState(button, classesToAdd, classesToRemove, textContent) {
    button.classList.add(...classesToAdd);
    button.classList.remove(...classesToRemove);
    button.textContent = textContent;
}

function fetchProgress(sequenceId, downloadFinished) {
    const progressBarContainer = document.getElementById('progressBarContainer_' + sequenceId);
    const progressBar = document.getElementById('progressBar_' + sequenceId);
    const progressCount = document.getElementById('progressCount_' + sequenceId);
    const downloadButton = document.getElementById('downloadButton_' + sequenceId);
    if (!progressBar) {
        console.log("Progress bar element not found for sequenceId: " + sequenceId);
        return;
    }

    if (!downloadButton) {
        console.log(sequenceId + " Already downloaded");
        storeData(sequenceId, false, false, true, false);
        clearInterval(loop[sequenceId]);
        return;
    }

    progressBar.parentElement.style.visibility = 'visible';
    progressBarContainer.classList.add('my-2');

    var existingEntries = JSON.parse(localStorage.getItem("allEntries"));

    if (downloadFinished) {
        clearInterval(loop[sequenceId]);
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
    })
};


function downloadSeq(sequenceId) {
    const button = document.getElementById('downloadButton_' + sequenceId);
    if (button) {
        handleButtonState(button, [buttonDisabledClass, buttonWarningClass], [buttonOutlineSecondaryClass], 'Downloading')
        storeData(sequenceId, uploadInProgress = false, downloadInProgress = true, downloadFinished = false, uploadFinished = false);
    }


    const progressBarContainer = document.getElementById('progressBarContainer_' + sequenceId);
    const progressBar = document.getElementById('progressBar_' + sequenceId);

    if (progressBar && progressBarContainer) {
        progressBar.parentElement.style.visibility = 'visible';
        progressBarContainer.classList.add('my-2');
    }

    fetch('/download-sequence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'sequence_id': sequenceId
        })
    }).then(response => {
        if (response.ok) {
            handleButtonState(button, [buttonSuccessClass, buttonDisabledClass], [buttonWarningClass, buttonDangerClass], 'Downloaded')
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Sequence ' + sequenceId + ' downloaded successfully!',
                timer: 2000,
                timerProgressBar: true,
                showConfirmButton: false,
                onClose: () => {
                    document.getElementById('disableUpload_' + sequenceId).classList.remove('disabled');
                    progressBar.parentElement.style.visibility = 'hidden';
                    progressBarContainer.classList.remove('my-2');
                    downloadFinished = true;
                    storeData(sequenceId, false, false, true, false);
                    if (downloadFinished) {
                        clearInterval(loop[sequenceId]);
                    }
                }
            });
        } else {
            handleButtonState(button, [buttonDangerClass], [buttonDisabledClass, buttonWarningClass], 'Failed, Try again.')
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Failed to download sequence ' + sequenceId + '. You can try again.'
            });
        }
    }).catch(error => {
        console.error('Error during sequence download:', error);
        if (button) {
            handleButtonState(button, [buttonWarningClass], [buttonDisabledClass], 'Error, Try again.')
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error during sequence download. Please try again.'
            });
        }
    });
}


function storeData(sequenceId, uploadInProgress, downloadInProgress, downloadFinished, uploadFinished) {
    var existingEntries = JSON.parse(localStorage.getItem("allEntries")) || [];
    var foundEntryIndex = existingEntries.findIndex(entry => entry.seqId === String(sequenceId));

    if (foundEntryIndex === -1) {
        var entry = {
            "seqId": sequenceId,
            "uploadInProgress": uploadInProgress,
            "downloadInProgress": downloadInProgress,
            "downloadFinished": downloadFinished,
            "uploadFinished": uploadFinished,
        };
        existingEntries.push(entry);
    } else {
        existingEntries[foundEntryIndex].uploadInProgress = uploadInProgress;
        existingEntries[foundEntryIndex].downloadInProgress = downloadInProgress;
        existingEntries[foundEntryIndex].downloadFinished = downloadFinished;
        existingEntries[foundEntryIndex].uploadFinished = uploadFinished;
    }

    localStorage.setItem("allEntries", JSON.stringify(existingEntries));
}



loop = {}
function downloadSequence(sequenceId, uploadInProgress = false, downloadInProgress = false, downloadFinished = false, uploadFinished = false) {
    storeData(sequenceId, uploadInProgress, downloadInProgress, downloadFinished, uploadFinished);
    downloadSeq(sequenceId);

    loop[sequenceId] = setInterval(function () {
        fetchProgress(sequenceId, downloadFinished);
    }, 2000);
}

function downloadAll() {
    var downloadButtons = document.querySelectorAll('[id^="downloadButton"]');
    if (downloadButtons.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: 'No items to download found on this page!',
            showCancelButton: false,
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
        });
        return;
    }
    downloadButtons.forEach(function (button) {
        if (!button.classList.contains('disabled')) {
            button.click();
        }
    });
}

function uploadAll() {
    var uploadButtons = document.querySelectorAll('[id^="uploadButton"]');
    var disabledButtons = document.querySelectorAll('[id^="disableUpload"]');

    var enabledDisabledButtons = Array.from(disabledButtons).filter(function(button) {
        return !button.classList.contains('disabled');
    });

    if (uploadButtons.length === 0 && enabledDisabledButtons.length === 0) {
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: 'No items to upload found on this page!',
            showCancelButton: false,
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
        });
        return;
    }

    uploadButtons.forEach(function (button) {
        if (!button.classList.contains('disabled')) {
            button.click();
        }
    });

    disabledButtons.forEach(function (button) {
        if (!button.classList.contains('disabled')) {
            button.click();
        }
    });
}



function uploadSequence(sequenceId, button) {
    handleButtonState(button, [buttonDisabledClass, buttonWarningClass], [buttonOutlineSecondaryClass], 'Uploading')
    storeData(sequenceId, uploadInProgress = true, downloadInProgress = false, downloadFinished = true, uploadFinished = false);

    fetch('/upload-sequence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'sequence_id': sequenceId
        })
    }).then(response => {
        return response.json();
    }).then(data => {
        if (data.status === 'success') {
            handleButtonState(button, [buttonSuccessClass, buttonDisabledClass], [buttonDangerClass, buttonWarningClass], 'Uploaded')
            uploadFinished = true;
            storeData(sequenceId, false, false, true, true);

            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Sequence ' + sequenceId + ' uploaded successfully!',
                showCancelButton: false,
                showConfirmButton: false,
                timer: 2000,
                timerProgressBar: true
            });
        } else {
            handleButtonState(button, [buttonDangerClass], [buttonDisabledClass, buttonWarningClass], 'Failed, Try again.')
            uploadFinished = false;
            storeData(sequenceId, false, false, true, false);

            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Sequence ' + sequenceId + ' could not be uploaded. ' + data.message
            });
        }
    }).catch(error => {
        console.error('Error during sequence upload:', error);
        handleButtonState(button, [buttonWarningClass], [buttonDisabledClass, buttonWarningClass], 'Error, Try again.')

        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Error during sequence upload. Please try again.'
        });
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
        Swal.fire({
            icon: 'warning',
            title: 'Warning',
            text: 'Please enter start and end sequence Number IDs.'
        });
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
    cards.forEach(function (card) {
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

function getUserInfo() {
    const infomessage = document.getElementById('info-message');
    infomessage.disabled = true;
    infomessage.textContent = 'Sequences are being fetched...';
    infomessage.style.display = 'block';
    document.getElementById("fetchButton").disabled = true;
    username = window.localStorage.getItem("user_name");
    fetch('/get-user-sequences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'user_name': username
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message);
            });
        }
        return response.json();
    })
    .then(data => {
        infomessage.textContent = 'Sequences fetched successfully!';
        infomessage.classList.add('alert', 'alert-success');
        setTimeout(() => {
            infomessage.style.display = 'none';
            window.location.reload();
        }, 1300);
    })
    .catch(error => {
        console.error('Error:', error);
        infomessage.textContent = 'Error fetching sequences: ' + error.message;
        infomessage.style.display = 'block';
        infomessage.classList.add('alert', 'alert-danger', 'mt-3');
    });
}


function getMissingSequences() {
    const infoMessageMissing = document.getElementById('info-message-missing')
    infoMessageMissing.textContent = 'Sequences are being fetched...';
    infoMessageMissing.classList.add('alert', 'alert-info');
    infoMessageMissing.classList.remove('alert-warning', 'alert-success');
    infoMessageMissing.style.display = 'block';
    infoMessageMissing.disabled = true;
    username = window.localStorage.getItem("user_name");

    fetch('/get-missing-sequences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'user_name': username
        })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Response was not ok.');
            }
            return response.json();
        })
        .then(data => {
            infoMessageMissing.textContent = 'Sequences fetched successfully!';
            infoMessageMissing.classList.remove('alert', 'alert-info', 'alert-warning');
            infoMessageMissing.classList.add('alert', 'alert-success');
            setTimeout(() => {
                infoMessageMissing.style.display = 'none';
                window.location.reload();
            }, 1300);
        })
        .catch(error => {
            console.error('Error:', error);
            infoMessageMissing.textContent = 'Error fetching sequences: ' + error.message;
            infoMessageMissing.style.display = 'block';
            infoMessageMissing.classList.remove('alert', 'alert-info', 'alert-warning');
            infoMessageMissing.classList.add('alert', 'alert-danger', 'mt-3');
        });
}


(function () {
    let activeseq = JSON.parse(localStorage.getItem("allEntries"));

    if (activeseq) {
        activeseq.forEach(entry => {
            const sequenceId = entry["seqId"];
            const isDownloadInProgress = entry["downloadInProgress"];
            const isUploadInProgress = entry["uploadInProgress"];

            if (isDownloadInProgress) {
                downloadSequence(sequenceId, false, true, false, false);
                const progressBar = document.getElementById('progressBar_' + sequenceId);
                const progressBarContainer = document.getElementById('progressBarContainer_' + sequenceId);
                const downloadButton = document.getElementById('downloadButton_' + sequenceId);

                if (progressBar && progressBarContainer) {
                    progressBar.parentElement.style.visibility = 'visible';
                    progressBarContainer.classList.add('my-2');
                }

                if (downloadButton) {
                    handleButtonState(downloadButton, [buttonDisabledClass, buttonWarningClass], [buttonOutlineSecondaryClass], 'Downloading')
                }
            }

            const uploadButton = document.getElementById('uploadedButton_' + sequenceId)
            if (uploadButton) {
                console.log(sequenceId + " Already uploaded");
                storeData(sequenceId, false, false, true, true);
                clearInterval(loop[sequenceId]);
                return;
            }

            if (isUploadInProgress) {
                const uploadButton = document.getElementById('uploadButton_' + sequenceId);

                if (uploadButton) {
                    uploadButton.click()
                }
            }

        });
    } else {
        console.error("No active sequences found.");
    }
})();


document.addEventListener("DOMContentLoaded", function () {
    const allProgressBars = document.querySelectorAll('.progress-bar');
    allProgressBars.forEach(function (progressBar) {
        progressBar.parentElement.style.visibility = 'hidden';
    });

    const clickHereElement = document.getElementById("clickHere");

    clickHereElement.addEventListener("click", function(event) {
      event.preventDefault();
      getMissingSequences();
    });
});
