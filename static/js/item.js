// In production uses wss, in development uses ws
var isProduction = window.location.hostname !== 'localhost';
var socket = io((isProduction ? 'wss://' : 'ws://') + window.location.host, {
	transports: ['websocket']
});

socket.on('connect', function() {
	console.log('WebSocket connection established');
});

socket.on('connect_error', function(error) {
	console.error('WebSocket connection failed: ', error);
	alert('WebSocket connection failed. Please try again later.');
	// Retry connection after 2 seconds
	setTimeout(function() {
		socket.connect();
	}, 5000);
});

// Create room for this item
var itemId = document.getElementById('item-id').value;
socket.emit('join_room', itemId);

socket.on('error', function(data) {
	console.log('Error: ', data.message);
});

socket.on('new_highest_bid', function(data) {
	console.log('New highest bid by ' + data.username + ': ' + data.bid);

	// Update highest bid on page
	var highestBidElement = document.getElementById('highest-bid');
	highestBidElement.textContent = data.bid;

	var bidderNameSpan = document.getElementById('bidder-name');
	var bidAmountSpan = document.getElementById('bid-amount');

	bidderNameSpan.textContent = data.username;
	bidAmountSpan.textContent = data.bid;

	// Show pop up gif for 2 seconds
	var popup = document.getElementById('pop-up');
	popup.style.display = 'block';
	setTimeout(function() {
		popup.style.display = 'none';
	}, 2000);

});

socket.on('new_bid', function(data) {
	console.log('New bid by ' + data.username + ': ' + data.bid);
	alert("Bid must be higher than current highest bid");
});

function placeBid() {
	var bidAmount = document.getElementById('bid-input').value;
	if (bidAmount == '') {
		alert('Please enter a valid bid amount');
		return;
	}
	var itemId = document.getElementById('item-id').value;
	socket.emit('place_bid', {item_id: itemId, bid_amount: bidAmount});
}