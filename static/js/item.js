// Websocket connection

var socket = io('wss://cse312barterplace.com', {
	transports: ['websocket']
});

// Create room for this item
var itemId = document.getElementById('item-id').value;
socket.emit('join_room', itemId);

socket.on('error', function(data) {
	console.log('Error: ', data.message);
});

socket.on('new_highest_bid', function(data) {
	console.log('New highest bid by ' + data.username + ': ' + data.bid);

	showBidNotification(data.bid, data.username);

	// Update highest bid on page
	var highestBidElement = document.getElementById('highest-bid');
	highestBidElement.textContent = data.bid;

	// Show pop up gif for 2 seconds
	var popup = document.getElementById('pop-up');
	popup.style.display = 'block';
	setTimeout(function() {
		popup.style.display = 'none';
	}, 2000);

});

socket.on('new_bid', function(data) {
	console.log('New bid place by ' + data.username + ' for ' + data.bid);
	showBidNotification(data.bid, data.username);
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

function showBidNotification(bidAmount, bidderName) {
	// Show new bid notification for 3 seconds
	var notification = document.getElementById('bid-notification');
	var bidAmountSpan = document.getElementById('bid-amount');
	var bidderNameSpan = document.getElementById('bidder-name');
	bidAmountSpan.textContent = bidAmount;
	bidderNameSpan.textContent = bidderName;
	notification.style.display = 'block';
	setTimeout(function() {
		notification.style.display = 'none';
	}, 3000);
}