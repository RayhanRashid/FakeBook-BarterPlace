// Websocket connection

var socket = io('http://localhost:8080', {
	transports: ['websocket']
});

socket.on('error', function(data) {
	console.log('Error: ', data.message);
});

socket.on('new_highest_bid', function(data) {
	console.log('New highest bid by ' + data.username + ': ' + data.bid);
	// Handle new highest bid
});

socket.on('new_bid', function(data) {
	console.log('New bid place by ' + data.username + ' for ' + data.bid);
	// Handle new bid
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