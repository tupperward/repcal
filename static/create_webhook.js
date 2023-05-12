document.addEventListener('DOMContentLoaded', function() {
  // Function to update the cron schedule based on the selected values
  function updateCronSchedule() {
    var timezone = document.getElementById('timezone').value;
    var hour = document.getElementById('hour').value;
    var minute = document.getElementById('minute').value;
    var cronSchedule = minute + ' ' + hour + ' * * *';

    document.getElementById('cronSchedule').value = cronSchedule;
  }

  // Event listeners for the form inputs
  document.getElementById('timezone').addEventListener('change', updateCronSchedule);
  document.getElementById('hour').addEventListener('change', updateCronSchedule);
  document.getElementById('minute').addEventListener('change', updateCronSchedule);

  // Submit event handler for the form
  document.getElementById('webhookForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Retrieve form values
    var name = document.getElementById('name').value;
    var webhookUrl = document.getElementById('webhookUrl').value;
    var cronSchedule = document.getElementById('cronSchedule').value;

    // Create URLSearchParams object with form data
    var formData = new URLSearchParams();
    formData.append('name', name);
    formData.append('webhookUrl', webhookUrl);
    formData.append('cronSchedule', cronSchedule);

    // Send data to the server using fetch
    fetch('/create_webhook', {
      method: 'POST',
      body: formData
    })
    .then(function(response) {
      if (response.ok) {
        // Handle success response here
        console.log(response);
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
