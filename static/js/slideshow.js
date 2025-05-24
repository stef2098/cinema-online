let currentSlide = 1;

function next() {
    hideCurrent();
    currentSlide++;
    if(currentSlide == 5)
        currentSlide = 1;
    showCurrent();
}

function prev() {
    hideCurrent();
    currentSlide--;
    if(currentSlide == 0)
        currentSlide = 4;
    showCurrent();
}

function hideCurrent() {
    document.getElementById('slide'+currentSlide).style.display = 'none';
}

function showCurrent() {
    document.getElementById('slide'+currentSlide).style.display = 'block';
}