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

document.getElementById('rec-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const criterionSelect = document.getElementById('criteria-select').value;
    const userInput = document.getElementById('criteria-input').value;
    const outputDiv = document.getElementById('recommendation-output');
    const modal = document.getElementById('recommendation-modal');

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
            outputDiv.innerHTML = '';

            if (data.recommendations && data.recommendations.length > 0) {
                data.recommendations.forEach(rec => {
                    const movieDiv = document.createElement('div');
                    movieDiv.className = 'movie-item';

                    const movieTitle = document.createElement('h3');
                    movieTitle.textContent = rec.title;
                    movieDiv.appendChild(movieTitle);

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

                    outputDiv.appendChild(movieDiv);
                });

                modal.style.display = 'block';
            } else {
                const noRecText = document.createElement('p');
                noRecText.textContent = 'No recommendations found for the given input.';
                outputDiv.appendChild(noRecText);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'An error occurred while processing your request.');
        });
});


document.getElementById('close-modal').addEventListener('click', function () {
    document.getElementById('recommendation-modal').style.display = 'none';
});



let errorTimeout;
function showError(message) {
    const errorContainer = document.getElementById('error-output');

    if (!errorContainer) {
        console.error('Error container not found in the DOM.');
        return;
    }

    errorContainer.innerHTML = `<p class="error-message">${message}</p>`;
    errorContainer.style.display = 'flex';
    errorContainer.classList.add('fadeInUp');

    if (errorTimeout) {
        clearTimeout(errorTimeout);
    }

    errorTimeout = setTimeout(() => {
        closeError(); 
    }, 3000);
}


function closeError() {
    const errorContainer = document.getElementById('error-output');
    errorContainer.style.display = 'none';
}