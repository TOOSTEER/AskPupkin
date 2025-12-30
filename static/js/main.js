document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.like-btn[data-question-id]').forEach(button => {
        button.addEventListener('click', function () {
            const questionId = this.dataset.questionId;
            const value = this.dataset.value;

            if (!questionId || !value) return;

            fetch(`/question/${questionId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ value: parseInt(value) })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const counter = document.querySelector(`.like-count[data-question-id="${questionId}"]`);
                        if (counter) {
                            counter.textContent = data.new_rating;
                        }
                        updateLikeButtons(questionId, value, 'question');
                    } else {
                        if (data.redirect) {
                            window.location.href = '/login/';
                        } else {
                            alert(data.error || 'An error occurred');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error sending request');
                });
        });
    });

    document.querySelectorAll('.like-btn[data-answer-id]').forEach(button => {
        button.addEventListener('click', function () {
            const answerId = this.dataset.answerId;
            const value = this.dataset.value;

            if (!answerId || !value) return;

            fetch(`/answer/${answerId}/like/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ value: parseInt(value) })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const counter = document.querySelector(`.like-count[data-answer-id="${answerId}"]`);
                        if (counter) {
                            counter.textContent = data.new_rating;
                        }
                        updateLikeButtons(answerId, value, 'answer');
                    } else {
                        if (data.redirect) {
                            window.location.href = '/login/';
                        } else {
                            alert(data.error || 'An error occurred');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error sending request');
                });
        });
    });

    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        let timeoutId;

        searchInput.addEventListener('input', function () {
            clearTimeout(timeoutId);

            timeoutId = setTimeout(() => {
                const query = this.value.trim();

                if (query.length < 2) {
                    hideSuggestions();
                    return;
                }

                fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        showSuggestions(data.suggestions, query);
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            }, 300);
        });

        document.addEventListener('click', function (event) {
            if (!event.target.closest('.search-container')) {
                hideSuggestions();
            }
        });
    }

    const tagsInput = document.getElementById('id_tags_input');
    if (tagsInput) {
        tagsInput.addEventListener('input', function () {
            const tags = this.value.split(',').map(tag => tag.trim());

            if (tags.length > 3) {
                this.value = tags.slice(0, 3).join(', ');
                showTagLimitWarning();
            }
        });
    }

    function updateLikeButtons(id, value, type) {
        const selector = type === 'question' ?
            `.like-btn[data-question-id="${id}"]` :
            `.like-btn[data-answer-id="${id}"]`;

        document.querySelectorAll(selector).forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.dataset.value) === parseInt(value)) {
                btn.classList.add('active');
            }
        });
    }

    function showTagLimitWarning() {
        let warning = document.getElementById('tag-limit-warning');
        if (!warning) {
            warning = document.createElement('div');
            warning.id = 'tag-limit-warning';
            warning.className = 'alert alert-warning mt-2';
            warning.textContent = 'You can specify up to 3 tags';

            const form = tagsInput.closest('form');
            form.insertBefore(warning, tagsInput.nextElementSibling);

            setTimeout(() => {
                warning.remove();
            }, 3000);
        }
    }

    function showSuggestions(suggestions, query) {
        let container = document.getElementById('search-suggestions');
        if (!container) {
            container = document.createElement('div');
            container.id = 'search-suggestions';
            container.className = 'search-suggestions';

            const searchContainer = searchInput.closest('.search-container') ||
                searchInput.closest('.d-flex');
            if (searchContainer) {
                searchContainer.style.position = 'relative';
                searchContainer.appendChild(container);
            }
        }

        if (suggestions.length === 0) {
            container.innerHTML = '<div class="suggestion-item">No results found</div>';
        } else {
            container.innerHTML = suggestions.map(suggestion =>
                `<a href="${suggestion.url}" class="suggestion-item">${highlightText(suggestion.text, query)}</a>`
            ).join('');
        }

        container.style.display = 'block';
    }

    function hideSuggestions() {
        const container = document.getElementById('search-suggestions');
        if (container) {
            container.style.display = 'none';
        }
    }

    function highlightText(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<strong>$1</strong>');
    }

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
});