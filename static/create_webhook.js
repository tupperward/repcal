document.addEventListener('DOMContentLoaded', function() {
  // Function to update the cron schedule based on the selected values
  function updateData() {
    // Update schedule and other data here
  }

  // Event listener for the form submit button
  document.getElementById('submit-button').addEventListener('click', function(e) {
    e.preventDefault();

    // Retrieve form values
    var baseUrl = window.location.origin
    var name = document.getElementById('name').value;
    var url = document.getElementById('url').value;
    var timezone = document.getElementById('timezone').value;
    var time = document.getElementById('time').value;

    // Extract hour and minute from the time string
    var [hour, minute, meridian] = time.split(':');
    hour = parseInt(hour);
    minute = parseInt(minute);

    // Convert hour to 24-hour format if needed (for AM/PM selection)
    if (meridian === 'PM' && hour < 12) {
      hour += 12;
    } else if (meridian === 'AM' && hour === 12) {
      hour = 0;
    }

    // Create cron string
    var schedule = minute + ' ' + hour + ' * * *';

    // Create URLSearchParams object with form data
    var formData = new URLSearchParams();
    formData.append('name', name);
    formData.append('url', url);
    formData.append('timezone', timezone);
    formData.append('schedule', schedule);

    // Send data to the server using fetch
    fetch('/create_webhook', {
      method: 'POST',
      body: formData
    })
    .then(function(response) {
      if (response.ok) {
        // Handle success response here
        console.log(response);
        window.location.assign(baseUrl + "/today");
      } else {
        // Handle error response here
        console.error('Failed to create webhook.');
      }
    })
    .catch(function(error) {
      // Handle network or other errors here
      console.error('An error occurred while creating webhook:', error);
    });
  });

  // Event listeners for the form inputs
  document.getElementById('name').addEventListener('change', updateData);
  document.getElementById('url').addEventListener('change', updateData);
  document.getElementById('timezone').addEventListener('change', updateData);
  document.getElementById('time').addEventListener('change', updateData);
});
