document.getElementById('criteria-select').addEventListener('change', function(e) {
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
            hintMessage = 'Provide a brief description or details about the movie plot.';
            break;
        case '2':
            placeholderText = 'Enter content rating';
            hintMessage = 'Specify the content rating: G, PG, PG-13, NR or R';
            break;
        case '3':
            placeholderText = 'Enter genre';
            hintMessage = 'Mention the genre that interests you.<br> You can choose: Action, Adventure, Animation, Art House, Classics, Comedy, Documentary, Drama, Family, Fantasy, Horror, International, Kids, Musical, Mystery, Romance, Science Fiction, Special Interest, Sports, Television, Western';
            break;
        case '4':
            placeholderText = 'Enter author name';
            hintMessage = 'Input the name of the movie director or writer.';
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
            hintMessage = 'Input the name of the production company (e.g., Warner Bros).';
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

document.getElementById('rec-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const criterionSelect = document.getElementById('criteria-select').value;
    const userInput = document.getElementById('criteria-input').value;
    const outputDiv = document.getElementById('recommendation-output');

    if (criterionSelect === "Select a criterion for building a recommendation") {
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
            const box = document.createElement('div');
            box.className = 'recommendation-box';

            data.recommendations.forEach(rec => {
                const recommendation = document.createElement('p');
                recommendation.textContent = rec;
                box.appendChild(recommendation);
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