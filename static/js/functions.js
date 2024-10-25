let dialog = document.getElementById('login_dialog');
let loginBtn = document.getElementById('login_button');
let home_post_button = document.getElementById('unlogged-post')
let close_button_login = document.getElementById('close_button_login');
let close_button_register = document.getElementById('close_button_register');

//show the modal when the login button is clicked
loginBtn.onclick = function() {
    dialog.showModal();
}

home_post_button.onclick = function(){
    dialog.showModal();
}

// close the modal when the 'x' is clicked in the modal 
close_button_login.onclick = function() {
    dialog.close();
}

close_button_register.onclick = function() {
    document.getElementById('register_dialog').close();
}

document.getElementById("register_link").addEventListener("click", function() {
    // close the login modal so that the register modal can open
    document.getElementById("login_dialog").close();
    
    // Open the register modal
    document.getElementById("register_dialog").showModal();
});

function toggleLike(button) {
    const itemId = button.getAttribute('data-item-id');
    const requestData = { item_id: itemId };
    
    fetch('/like', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { 
                alert(err.error);  // Show error message to user
                throw new Error('Network response was not ok.'); 
            });
        }
        return response.json();
    })
    .then(data => {
        // Update button state and text based on the like status
        if (data.status === 'liked') {
            button.classList.add('liked');
            button.nextElementSibling.textContent = "You've liked this post";
        } else {
            button.classList.remove('liked');
            button.nextElementSibling.textContent = "Like this post";
        }

        // Update the like count
        const likeCountSpan = document.getElementById(`like-count-${itemId}`);
        likeCountSpan.textContent = parseInt(likeCountSpan.textContent) + (data.status === 'liked' ? 1 : -1);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}