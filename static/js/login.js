$("#login-form").submit(function(event) {
    event.preventDefault();
    $.post("/api/login", $(this).serialize(), function(data) {
        $("#message").html(data.message);
        if (data.message === "Logged in successfully") {
            window.location.href = "/dashboard";
        }
    }).fail(function(data) {
        $("#message").html(data.responseJSON.error);
    });
});
