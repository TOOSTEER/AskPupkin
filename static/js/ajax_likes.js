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

    function updateLikeButton(button, userValue) {
        button.classList.remove('active', 'liked', 'disliked');

        if (userValue === 1) {
            button.classList.add('active', 'liked');
        } else if (userValue === -1) {
            button.classList.add('active', 'disliked');
        }
    }

    function loadLikeStatus() {
        document.querySelectorAll('[data-question-id]').forEach(button => {
            const questionId = button.dataset.questionId;
            if (questionId) {
                fetch(`/check_like_status/?question_id=${questionId}`, {
                    headers: {
                        'X-CSRFToken': csrftoken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.authenticated && data.question_like !== undefined) {
                            updateLikeButton(button, data.question_like);
                        }
                    });
            }
        });

        document.querySelectorAll('[data-answer-id]').forEach(button => {
            const answerId = button.dataset.answerId;
            if (answerId) {
                fetch(`/check_like_status/?answer_id=${answerId}`, {
                    headers: {
                        'X-CSRFToken': csrftoken
                    }
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.authenticated && data.answer_like !== undefined) {
                            updateLikeButton(button, data.answer_like);
                        }
                    });
            }
        });
    }

    loadLikeStatus();

    function sendLikeRequest(url, value, counter, type, elementId) {
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ value: parseInt(value) })
        })
            .then(response => {
                if (response.status === 403) {
                    window.location.href = '/login/';
                    return Promise.reject('Требуется авторизация');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    if (counter) {
                        counter.textContent = data.new_rating;
                    }

                    updateLikeButton(document.querySelector(`[data-${type}-id="${elementId}"]`), data.user_value);

                    const oppositeButton = document.querySelector(`[data-${type}-id="${elementId}"][data-value="${-value}"]`);
                    if (oppositeButton) {
                        updateLikeButton(oppositeButton, 0);
                    }
                } else {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        alert(data.error || 'Произошла ошибка');
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (error !== 'Требуется авторизация') {
                    alert('Произошла ошибка при отправке запроса');
                }
            });
    }

    document.querySelectorAll('.like-btn[data-question-id]').forEach(button => {
        button.addEventListener('click', function () {
            const questionId = this.dataset.questionId;
            const value = this.dataset.value;
            const counter = document.querySelector(`.question-rating[data-question-id="${questionId}"]`);

            sendLikeRequest(`/question/${questionId}/like/`, value, counter, 'question', questionId);
        });
    });

    document.querySelectorAll('.like-btn[data-answer-id]').forEach(button => {
        button.addEventListener('click', function () {
            const answerId = this.dataset.answerId;
            const value = this.dataset.value;
            const counter = document.querySelector(`.answer-rating[data-answer-id="${answerId}"]`);

            sendLikeRequest(`/answer/${answerId}/like/`, value, counter, 'answer', answerId);
        });
    });

    document.querySelectorAll('.mark-correct-btn').forEach(button => {
        button.addEventListener('click', function () {
            const answerId = this.dataset.answerId;
            markAnswerCorrect(answerId, this);
        });
    });

    function markAnswerCorrect(answerId, buttonElement) {
        fetch(`/answer/${answerId}/correct/ajax/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        })
            .then(response => {
                if (response.status === 403) {
                    alert('Вы не автор этого вопроса');
                    return Promise.reject('Недостаточно прав');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const answerElement = buttonElement.closest('.answer');
                    answerElement.classList.add('correct');

                    document.querySelectorAll('.mark-correct-btn').forEach(btn => {
                        btn.remove();
                    });

                    const badge = document.createElement('span');
                    badge.className = 'badge bg-success ms-2';
                    badge.textContent = '✓ Правильный ответ';
                    answerElement.querySelector('.answer-header').appendChild(badge);

                    alert('Ответ отмечен как правильный!');
                } else {
                    alert(data.error || 'Произошла ошибка');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (error !== 'Недостаточно прав') {
                    alert('Произошла ошибка при отправке запроса');
                }
            });
    }

    window.likeManager = {
        loadLikeStatus,
        sendLikeRequest,
        markAnswerCorrect
    };
});