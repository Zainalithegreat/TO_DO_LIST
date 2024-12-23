function draggable() {
  const draggables = document.querySelectorAll('.draggable')
  const containers = document.querySelectorAll('.container')

  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', () => {
      draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', () => {
      draggable.classList.remove('dragging')
    })
  })

  containers.forEach(container => {
    container.addEventListener('dragover', e => {
      e.preventDefault()
      const draggable = document.querySelector('.dragging')
      container.appendChild(draggable)
    })
  })
}

function create(){
  const container = document.getElementById("container-1");
  const input = document.createElement("textarea");
  input.className = "draggable";

  input.type = "text";
  input.placeholder = "message"
  input.draggable = true;

  container.appendChild(input);
  draggable();
}
function resize() {
    const textareas = document.getElementsByClassName('resizableTextarea');
    Array.from(textareas).forEach(textarea => {
        textarea.style.overflow = 'hidden'; // Prevent scrollbars from appearing
        textarea.addEventListener('input', () => {
            textarea.style.height = 'auto'; // Reset height to auto to calculate new height
            textarea.style.height = textarea.scrollHeight + 'px'; // Adjust height based on content
        });
    });
}

document.addEventListener('DOMContentLoaded', function() {
      const button = document.getElementById("add-input-btn");
      button.addEventListener("click", create);
      resize()
      draggable();  // Call the draggable function
    });