let timeout;

// Utility: Debounce function
function debounce(func, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

function initializeDragAndDrop() {
  // Prevent duplicate event listeners by marking initialized elements
  const containers = document.querySelectorAll('.container:not(.initialized)');
  containers.forEach((container) => {
    container.classList.add('initialized');

    container.addEventListener('dragover', (e) => {
      e.preventDefault(); // Allow drop
      container.classList.add('highlight');
    });

    container.addEventListener('dragleave', () => {
      container.classList.remove('highlight');
    });

    container.addEventListener('drop', (e) => {
      e.preventDefault();
      const draggingElement = document.querySelector('.dragging');
      if (draggingElement) {
        container.appendChild(draggingElement); // Move the element
        container.classList.remove('highlight');

        // Update backend with new container info
        updateContainer(draggingElement.id, container.id);
      }
    });
  });

  // Initialize only new draggable elements
  document.querySelectorAll('.draggable:not(.initialized)').forEach((draggable) => {
    draggable.classList.add('initialized');
    draggable.addEventListener('dragstart', () => {
      draggable.classList.add('dragging');
    });

    draggable.addEventListener('dragend', () => {
      draggable.classList.remove('dragging');
    });
  });
}

async function createNewTextarea() {
  try {
    const response = await fetch('/get-new-message-id');
    if (!response.ok) throw new Error('Failed to fetch new message ID');

    const { newMessageId } = await response.json();
    const container = document.getElementById('container-1');
    const textarea = document.createElement('textarea');
    const div = document.createElement("div");
    const button = document.createElement("button")



    textarea.id = newMessageId;
    textarea.placeholder = 'Enter your message here...';

    div.id = newMessageId
    div.className = 'draggable resizableTextarea';
    div.draggable = true

    button.className = 'remove_button';

    div.appendChild(textarea)
    div.appendChild(button)

    // Auto-resize height based on content
    textarea.style.overflow = 'hidden';
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    });

    container.appendChild(div);

    // Initialize drag-and-drop for the new textarea
    initializeDragAndDrop();
  } catch (error) {
    console.error('Error creating new textarea:', error);
  }
}

// Update container information in the backend
async function updateContainer(textareaId, newContainerId) {
  const data = { textarea_id: textareaId, new_container: newContainerId };

  try {
    const response = await fetch('/update-message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to update container');
    }
    console.log('Container updated successfully:', data);
  } catch (error) {
    console.error('Error updating container:', error);
  }
}


document.addEventListener('input', debounce(async (e) => {
  const newValue = e.target.value;
  const draggableElement = e.target.closest(".draggable");
  const containerElement = e.target.closest(".container");

  // Ensure that both the textarea and the container are valid
  const containerId = containerElement?.id;
  const id = draggableElement?.id;

  if (!containerId || !id) {
    console.error("Missing container or message ID");
    return; // Exit if there's no valid container or draggable element
  }

  const data = { id, text: newValue, containerId };

  console.log('Sending data:', data); // Log the data being sent

  try {
    const response = await fetch('/save-message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.log('Error data:', errorData); // Log the error response

      if (errorData.error === "Message already exists") {
        console.log("Message already exists");
        e.target.remove(); // Remove the textarea element from the DOM
      } else {
        throw new Error('Failed to save changes');
      }
    } else {
      console.log('Changes saved successfully:', data);
    }
  } catch (error) {
    console.error('Error saving changes:', error);
  }
}, 500));


// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
  const addInputButton = document.getElementById('add-input-btn');
  addInputButton.addEventListener('click', createNewTextarea);

  initializeDragAndDrop(); // Set up drag-and-drop functionality
});
