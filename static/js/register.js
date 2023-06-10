$(document).ready(function() {
    $('#register-form').submit(function(event) {
        event.preventDefault();

        var username = $('#username').val();
        var email = $('#email').val();
        var password = $('#password').val();
        var confirm = $('#confirm').val();

        if (password !== confirm) {
            alert('Password and Confirm Password must match.');
            return;
        }

        $.ajax({
            type: 'POST',
            url: '/api/register',
            contentType: 'application/json',
            data: JSON.stringify({
                username: username,
                email: email,
                password: password
            }),
            success: function(response) {
                alert('Registered successfully.');
                window.location.href = '/login';
            },
            error: function(xhr, status, error) {
                var errorMessage;
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                } else {
                    errorMessage = 'Registration failed. Please try again.';
                }
                alert(errorMessage.toString());
            }
        });
    });
});
