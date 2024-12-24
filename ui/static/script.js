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

async function getNewMessageId() {
  try {
    const response = await fetch('/get-new-message-id');
    if (!response.ok) throw new Error('Failed to fetch new message ID');

    const data = await response.json();
    return data.newMessageId;  // Return the new message ID from the response
  } catch (error) {
    console.error('Error fetching new message ID:', error);
    return null;  // Return null if there's an error
  }
}

function create() {
  getNewMessageId().then((newMessageId) => {
    const initialContainerId = 'container-1';
    const container = document.getElementById(initialContainerId);
    const input = document.createElement('textarea');

    // Assign unique ID and classes
    input.className = 'draggable resizableTextarea';
    input.id = newMessageId;
    input.placeholder = 'Enter your message here...';
    input.draggable = true;

    // Attach input event listener for saving updates
    input.addEventListener(
      'input',
      debounce(async (e) => {
        const newValue = e.target.value;
        const currentContainer = e.target.closest('.container')?.id || initialContainerId;

        const data = { id: newMessageId, text: newValue, containerId: currentContainer };

        try {
          const response = await fetch('/save-message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
          });

          if (!response.ok) {
            if (response.status === 409) {
              console.error('Duplicate message detected. Removing textarea.');
              input.remove();
              alert('Error: This message already exists.');
            } else {
              throw new Error('Failed to save changes.');
            }
          } else {
            console.log('Changes saved successfully:', data);
          }
        } catch (error) {
          console.error('Error saving changes:', error);
        }
      }, 500) // Debounce delay
    );

    // Automatically adjust textarea height
    input.style.overflow = 'hidden';
    input.addEventListener('input', () => {
      input.style.height = 'auto';
      input.style.height = `${input.scrollHeight}px`;
    });

    // Add to container
    container.appendChild(input);

    // Reinitialize draggable functionality
    draggable();
  });
}

// Update container ID on drop
function draggable() {
  const draggables = document.querySelectorAll('.draggable');
  const containers = document.querySelectorAll('.container');

  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', () => {
      draggable.classList.add('dragging');
    });

    draggable.addEventListener('dragend', async () => {
      const newContainer = document.querySelector('.container:hover');
      const textareaId = draggable.id;

      draggable.classList.remove('dragging');

      if (!newContainer || !textareaId) {
        console.log('No valid container or textarea ID found');
        return;
      }

      const newContainerId = newContainer.id;
      const data = { new_container: newContainerId, textarea_id: textareaId };

      try {
        const response = await fetch('/update-message', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error('Failed to send data');
        console.log('Container updated successfully:', data);
      } catch (error) {
        console.error('Error updating container:', error);
      }
    });
  });

  containers.forEach(container => {
    container.addEventListener('dragover', (e) => {
      e.preventDefault();
      const draggable = document.querySelector('.dragging');
      container.appendChild(draggable);
    });
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
//saving
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



// Debounce function to limit frequent saves
function debounce(func, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => func.apply(this, args), delay);
  };
}

//updating
document.addEventListener(
  "drop",
  debounce(async (e) => {
    // Find the closest container and draggable element
    const new_container = e.target.closest(".container")?.id;
    const draggableElement = e.target.closest(".draggable");
    const textarea_id = draggableElement?.id;

    if (!new_container || !textarea_id) {
      console.log("No valid container or textarea ID found");
      return; // Exit if no valid container or draggable element is found
    }

    const data = { new_container, textarea_id };

    try {
      const response = await fetch("/update-message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) throw new Error("Failed to send data");
      console.log("Changes saved successfully:", data);
    } catch (error) {
      console.error("Error saving changes:", error);
    }
  }, 100) // Debounce delay
);


document.addEventListener('DOMContentLoaded', function () {
  const button = document.getElementById('add-input-btn');
  button.addEventListener('click', create);
  draggable(); // Initialize draggable elements
});
