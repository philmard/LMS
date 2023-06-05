function showFlames(button) {
    const flames = document.createElement('div');
    flames.classList.add('flames');
    document.body.appendChild(flames);
    setTimeout(() => {
        document.body.removeChild(flames);
    }, 2000);
}

const borrowButtons = document.querySelectorAll('.borrow-button');
const returnButtons = document.querySelectorAll('.return-button');
const cancelButtons = document.querySelectorAll('.cancel-button');

borrowButtons.forEach(button => {
    button.addEventListener('click', () => {
        if (button.value === 'Borrow') {
            button.value = 'Returned';
        } else if (button.value === 'Returned') {
            button.value = 'cancel return';
        } else if (button.value === 'cancel borrow') {
            button.value = 'Borrow';
        }
    });
});

cancelButtons.forEach(button => {
    button.addEventListener('click', () => {
        const siblingButton = button.previousElementSibling;
        if (siblingButton && siblingButton.classList.contains('borrow-button')) {
            siblingButton.value = 'Borrow';
        } else if (siblingButton && siblingButton.classList.contains('return-button')) {
            siblingButton.value = 'Returned';
        }
    });
});

function goToHomePage() {
    window.location.href = "http://127.0.0.1:5000/home";
}
