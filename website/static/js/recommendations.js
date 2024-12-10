// Обработка выбора критерия
document.getElementById('criteria-select').addEventListener('change', function (e) {
    const selectedValue = e.target.value;
    console.log("Selected value:", selectedValue);

    const inputContainer = document.getElementById('input-container');
    const inputField = document.getElementById('criteria-input');
    const hintContainer = document.getElementById('hint-container');
    const hintText = document.getElementById('hint-text');

    let placeholderText = '';
    let hintMessage = '';

    switch (selectedValue) {
        case '1':
            placeholderText = 'Enter plot details';
            hintMessage = 'Enter the name of the movie whose plot you liked.';
            break;
        case '2':
            placeholderText = 'Enter content rating';
            hintMessage = 'Specify the content rating: G, PG, PG-13, NR or R';
            break;
        case '3':
            placeholderText = 'Enter genre';
            hintMessage = 'Enter the genre that interests you.<br> You can choose: Action, Adventure, Animation, Art House, Classics, Comedy, Documentary, Drama, Family, Fantasy, Horror, International, Kids, Musical, Mystery, Romance, Science Fiction, Special Interest, Sports, Television, Western';
            break;
        case '4':
            placeholderText = 'Enter author name';
            hintMessage = 'Enter the name of the movie director or writer.';
            break;
        case '5':
            placeholderText = 'Enter actor name';
            hintMessage = 'Provide the name of the actor you want to search movies for.';
            break;
        case '6':
            placeholderText = 'Enter release year';
            hintMessage = 'Enter the release year of the movies you are interested in.';
            break;
        case '7':
            placeholderText = 'Enter production company';
            hintMessage = 'Enter the name of the production company (e.g. Warner Bros).';
            break;
        default:
            inputContainer.style.display = 'none';
            hintContainer.style.display = 'none';
            return;
    }

    inputField.placeholder = placeholderText;
    hintText.innerHTML = hintMessage;

    inputContainer.style.display = 'block';
    hintContainer.style.display = 'block';
});

// Отправка формы для получения рекомендаций
document.getElementById('rec-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const criterionSelect = document.getElementById('criteria-select').value;
    const userInput = document.getElementById('criteria-input').value;
    const outputDiv = document.getElementById('recommendation-output');

    if (!criterionSelect || !userInput) {
        showError('Please select a criterion and provide input.');
        return;
    }

    fetch('/recommendations-system', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'criterion': criterionSelect,
            'criteria-input': userInput
        })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to fetch recommendations.');
                });
            }
            return response.json();
        })
        .then(data => {
            outputDiv.innerHTML = ''; // Очистить предыдущий вывод

            if (data.recommendations && data.recommendations.length > 0) {
                const box = document.createElement('div');
                box.className = 'recommendation-box';

                data.recommendations.forEach(rec => {
                    const movieDiv = document.createElement('div');
                    movieDiv.className = 'movie-item';

                    // Название фильма
                    const movieTitle = document.createElement('h3');
                    movieTitle.textContent = rec.title;
                    movieDiv.appendChild(movieTitle);

                    // Постер фильма
                    if (rec.poster_url) {
                        const moviePoster = document.createElement('img');
                        moviePoster.src = rec.poster_url;
                        moviePoster.alt = `Poster for ${rec.title}`;
                        moviePoster.className = 'movie-poster';
                        movieDiv.appendChild(moviePoster);
                    } else {
                        const noPosterText = document.createElement('p');
                        noPosterText.textContent = 'Poster not available';
                        movieDiv.appendChild(noPosterText);
                    }

                    box.appendChild(movieDiv);
                });

                outputDiv.appendChild(box);
            } else {
                showError('No recommendations found for the given input.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing your request.');
        });
});

// Функции для вывода ошибок
function showError(message) {
    const errorDiv = document.getElementById('error-output');
    errorDiv.innerHTML = `
        <p class="error-message">${message}</p>
        <button class="close-button" onclick="closeError()">✖</button>
    `;
    errorDiv.style.display = 'flex';

    setTimeout(() => {
        closeError();
    }, 5000);
}

function closeError() {
    const errorDiv = document.getElementById('error-output');
    errorDiv.style.display = 'none';
}
