document.addEventListener('DOMContentLoaded', function() {
  // Function to update the cron schedule based on the selected values
  // Function to update the cron schedule based on the selected values
  function updateData() {
    var name = document.getElementById('name').value;
    var url = document.getElementById('url').value;
    var timezone = document.getElementById('timezone').value;
    var time = document.getElementById('time').value;
    var [hour, minute] = time.split(':');
    var schedule = minute + ' ' + hour + ' * * *';

    document.getElementById('schedule').value = schedule;
  }

  // Event listeners for the form inputs
  document.getElementById('name').addEventListener('change', updateData);
  document.getElementById('url').addEventListener('change', updateData);
  document.getElementById('timezone').addEventListener('change', updateData);
  document.getElementById('time').addEventListener('change', updateData);

  // Submit event handler for the form
  document.getElementById('webhook-form').addEventListener('submit', function(e) {
    e.preventDefault();

    // Retrieve form values
    var name = document.getElementById('name').value;
    var url = document.getElementById('url').value;
    var timezone = document.getElementById('timezone').value;
    var schedule = document.getElementById('schedule').value;

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
        window.location.assign(url + "/today");
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
});
