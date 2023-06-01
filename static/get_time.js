// Get the local time and timezone offset
var localTime = Math.floor(Date.now() / 1000);
var timezoneOffset = new Date().getTimezoneOffset();

// Construct base URL
var url = window.location.origin;

// Send the local time and timezone offset to the Flask app using a POST request
fetch(url + "/local_time", {
    method: "POST",
    body: new URLSearchParams({
        local_time: localTime,
        timezone_offset: timezoneOffset,
    }),
    redirect: "follow",
})
    .then((response) => {
        // Handle the response from the Flask app
        if (response.ok) {
            window.location.assign(url + "/today");
        } else {
            console.error("Failed to send local time and timezone offset.");
        }
    })
    .catch((error) => {
        console.error("An error occurred while sending local time and timezone offset:", error);
    });
