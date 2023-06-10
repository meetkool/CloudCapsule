$(document).ready(function() {
    $.get("/api/task", function(data) {
        // Display the tasks in some way.
        // This will depend on how you choose to display the tasks in your HTML.
    }).fail(function(data) {
        if (data.responseJSON.error === "Please log in first") {
            window.location.href = "/login";
        } else {
            // Handle other types of errors.
        }
    });
});
