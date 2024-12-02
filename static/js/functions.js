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


// Make a request for /item/{itemId} when an item is clicked
function viewItem(itemId) {
    window.location.href = "/item/" + itemId;
}
