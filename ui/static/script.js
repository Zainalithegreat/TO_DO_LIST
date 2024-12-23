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

async function sendUpdate(containerId) {
  // Select all textareas within the specified container
  const container = document.getElementById(containerId);
  const textareas = container.querySelectorAll('textarea');

  textareas.forEach((textarea) => {
    // Attach an 'input' event listener to each textarea
    textarea.addEventListener(
      'input',
      debounce(async (e) => {
        const newValue = e.target.value;
        const id = e.target.value; // Use the unique identifier of the textarea

        // Prepare data to send
        const data = { id, text: newValue, containerId};


        try {
          // Send an asynchronous POST request
          const response = await fetch('/save-message', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
          });

          if (!response.ok) {
            throw new Error('Failed to save changes');
          }
          console.log('Changes saved successfully:', data);
        } catch (error) {
          console.error('Error saving changes:', error);
        }
      }, 500) // Debounce delay in milliseconds
    );
  });
}

// Debounce function to limit frequent saves
function debounce(func, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
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

document.addEventListener("input", function(){
    sendUpdate('container-1');
    sendUpdate('container-2');
    sendUpdate('container-3');
});