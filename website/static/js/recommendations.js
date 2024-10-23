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
            hintMessage = 'Specify the content rating (e.g., PG, PG-13, R).';
            break;
        case '3':
            placeholderText = 'Enter genre';
            hintMessage = 'Mention the genre (e.g., Action, Comedy, Drama) that interests you.';
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
            hintMessage = 'Enter the release year of the movie you are looking for.';
            break;
        case '7':
            placeholderText = 'Enter runtime (in minutes)';
            hintMessage = 'Specify the movie runtime in minutes (e.g., 120 for 2 hours).';
            break;
        case '8':
            placeholderText = 'Enter production company';
            hintMessage = 'Input the name of the production company (e.g., Warner Bros).';
            break;
        default:
            inputContainer.style.display = 'none';
            hintContainer.style.display = 'none';
            return;
    }

    inputField.placeholder = placeholderText;
    hintText.textContent = hintMessage;

    inputContainer.style.display = 'block';
    hintContainer.style.display = 'block';
});

document.getElementById('rec-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const criterionSelect = document.getElementById('criteria-select').value;
    const userInput = document.getElementById('criteria-input').value;
    const outputDiv = document.getElementById('recommendation-output');

    if (!userInput || criterionSelect === "Select a criterion for building a recommendation") {
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
    .then(response => response.json())
    .then(data => {
        outputDiv.innerHTML = '';
        const box = document.createElement('div');
        box.className = 'recommendation-box';

        if (data.recommendations) {
            data.recommendations.forEach(rec => {
                const recommendation = document.createElement('p');
                recommendation.textContent = rec;
                box.appendChild(recommendation);
            });
        } else {
            box.innerHTML = '<p>No recommendations found.</p>';
        }

        outputDiv.appendChild(box);
    })
    .catch(error => {
        console.error('Error:', error);
        showError('There was an error processing your request.');
    });
});


function showError(message) {
    const errorMessage = document.createElement('p');
    errorMessage.className = 'error-message';
    errorMessage.textContent = message;

    const outputDiv = document.getElementById('recommendation-output');
    outputDiv.innerHTML = '';
    outputDiv.appendChild(errorMessage);

    setTimeout(() => {
        outputDiv.innerHTML = '';
    }, 2000);
}
