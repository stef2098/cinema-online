let tickets = 0;
let seats = [];

for(let i = 0; i < 100; i++) {
    seats.push([])
    for(let j = 0; j < 100; j++) {
        seats[i].push(false)
    }
}

function decreaseTickets() {
    tickets = Math.max(tickets - 1, 0);
    updateTicketDisplay();
}

function increaseTickets() {
    tickets++;
    updateTicketDisplay();
}

function updateTicketDisplay() {
    //document.getElementById('tickets').innerHTML = 'Карте: '+tickets;
    document.getElementById('buy').innerHTML = 'Резервиши: ' + (tickets * price) + ' RSD';
}

function addseat(button, row, column) {
    if (row < 0 || column < 0)
        return
    seats[row][column] = !seats[row][column]
    if(seats[row][column]) {
        button.style.backgroundColor = 'white'
        increaseTickets()
    } else {
        button.style.backgroundColor = 'brown'
        decreaseTickets()
    }
}

document.getElementById('buy').addEventListener("click", () => {
    seatsForReservation = []
    for(let i = 0; i < 100; i++) {
        for(let j = 0; j < 100; j++) {
            if(seats[i][j])
                seatsForReservation.push([i, j])
        }
    }

    window.location.href = "/rezervisi/"+projection+"/"+seatsForReservation;
});