let draggableElements = null;
let dragSrcEl = null;
let lastOverEl = null;

function handleDragStart(e) {
    this.style.opacity = '0.4';  // this / e.target is the source node.

    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragEnter(e) {
    if (lastOverEl != this && lastOverEl != null) {
        lastOverEl.classList.remove('over');
    }

    this.classList.add('over');
    lastOverEl = this;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault(); // Necessary. Allows us to drop.
    }

    e.dataTransfer.dropEffect = 'move';  // See the section on the DataTransfer object.
    return false;
}

function handleDragLeave(e) {
    //this.classList.remove('over');  // this / e.target is previous target element.
}

function handleDrop(e) {
    // this / e.target is current target element.
    if (e.stopPropagation) {
        e.stopPropagation(); // Stops some browsers from redirecting.
    }

    // Don't do anything if dropping the same column we're dragging.
    if (dragSrcEl != this) {
        // Set the source column's HTML to the HTML of the column we dropped on.
        dragSrcEl.innerHTML = this.innerHTML;
        this.innerHTML = e.dataTransfer.getData('text/html');
    }

    return false;
}

function handleDragEnd(e) {
    // this/e.target is the source node.
    this.style.opacity = 1;

    draggableElements.forEach(function(draggable){
        draggable.classList.remove('over');
    });
}

function addDragListeners() {
    draggableElements = document.querySelectorAll('.draggable');

    draggableElements.forEach(function(draggable){
        draggable.addEventListener('dragstart', handleDragStart, false);
        draggable.addEventListener('dragenter', handleDragEnter, false);
        draggable.addEventListener('dragover', handleDragOver, false);
        draggable.addEventListener('dragleave', handleDragLeave, false);
        draggable.addEventListener('drop', handleDrop, false);
        draggable.addEventListener('dragend', handleDragEnd, false);
    });
}

