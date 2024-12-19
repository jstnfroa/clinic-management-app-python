// Get the modal
var modal = document.getElementById('staffModal');

// Get the button that opens the modal
var openModalBtn = document.getElementById('openModalBtn');

// Get the <span> element that closes the modal
var closeModalBtn = document.getElementById('closeModalBtn');

// When the user clicks the button, open the modal
openModalBtn.onclick = function() {
    modal.style.display = 'block';
}

// When the user clicks on <span> (x), close the modal
closeModalBtn.onclick = function() {
    modal.style.display = 'none';
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
