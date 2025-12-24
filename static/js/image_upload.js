document.addEventListener('DOMContentLoaded', function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function setupImagePreview(inputId, previewId) {
        const input = document.getElementById(inputId);
        const preview = document.getElementById(previewId);

        if (input && preview) {
            input.addEventListener('change', function () {
                const file = this.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function (e) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                    reader.readAsDataURL(file);
                } else {
                    preview.style.display = 'none';
                }
            });
        }
    }

    setupImagePreview('avatar-upload', 'avatar-preview');
    setupImagePreview('question-image-upload', 'question-image-preview');
    setupImagePreview('answer-image-upload', 'answer-image-preview');

    function validateImageSize(file, maxSizeMB) {
        const maxSizeBytes = maxSizeMB * 1024 * 1024;
        if (file.size > maxSizeBytes) {
            alert(`Размер изображения не должен превышать ${maxSizeMB}MB`);
            return false;
        }
        return true;
    }

    function validateImageType(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!validTypes.includes(file.type)) {
            alert('Поддерживаемые форматы: JPG, JPEG, PNG, GIF');
            return false;
        }
        return true;
    }

    const imageInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                if (!validateImageType(file)) {
                    this.value = '';
                    return;
                }

                const maxSize = this.id.includes('avatar') ? 2 : 5;
                if (!validateImageSize(file, maxSize)) {
                    this.value = '';
                    return;
                }
            }
        });
    });

    function uploadImage(formData, url, successCallback, errorCallback) {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    successCallback(data);
                } else {
                    errorCallback(data.error);
                }
            })
            .catch(error => {
                errorCallback('Произошла ошибка при загрузке изображения');
            });
    }

    window.imageUploader = {
        setupImagePreview,
        validateImageSize,
        validateImageType,
        uploadImage
    };
});