function reserveBook(event) {
    event.preventDefault(); // Prevent form submission

    const form = event.target;
    const isbn = form.querySelector('input[name="isbn"]').value;

    // Send a POST request to the server to create a reservation
    fetch('/create_reservation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ isbn }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response from the server (e.g., show success message, redirect, etc.)
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

  