// Retrieve local time from the browser
var localTime = Math.floor(Date.now() / 1000);

// Construct baseurl.
var url = window.location.origin;

// Send the local time to the Flask app using a POST request
fetch(url + "/get_local_time", {
    method: "POST",
    body: new URLSearchParams({
        local_time: localTime,
    }),
    redirect: "follow",
})
    .then((response) => {
        // Handle the response from the Flask app
        if (response.ok) {
            window.location.assign(url + "/today");
        } else {
            console.error("Failed to send local time.");
        }
    })
    .catch((error) => {
        console.error("An error occurred while sending local time:", error);
    });
