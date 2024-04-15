window.login = {};

login.bind_events = function() {
    $(".form-login").on("submit", function(event) {
        event.preventDefault();
        var args = {};
        args.cmd = "login";
        args.usr = frappe.utils.xss_sanitise(($("#login_email").val() || "").trim());
        args.pwd = $("#login_password").val();
        args.device = "desktop";
        if(!args.usr || !args.pwd) {
            frappe.msgprint('{{ _("Both login and password required") }}');
            return false;
        }
        login.call(args);
        return false;
    });

    $(".toggle-password").click(function() {
        $(this).toggleClass("fa-eye fa-eye-slash");
        var input = $($(this).attr("toggle"));
        if (input.attr("type") == "password") {
            input.attr("type", "text");
        } else {
            input.attr("type", "password");
        }
    });
}

// Login
login.call = function(args, callback) {
    return frappe.call({
        type: "POST",
        args: args,
        callback: callback,
        freeze: true,
        statusCode: login.login_handlers
    });
}

login.login_handlers = (function() {
    var get_error_handler = function(default_message) {
        return function(xhr, data) {
            if(xhr.responseJSON) {
                data = xhr.responseJSON;
            }

            var message = default_message;
            if (data._server_messages) {
                message = ($.map(JSON.parse(data._server_messages || '[]'), function(v) {
                    // temp fix for messages sent as dict
                    try {
                        return JSON.parse(v).message;
                    } catch (e) {
                        return v;
                    }
                }) || []).join('<br>') || default_message;
            }

            if(message===default_message) {
                // mach was
            } else {
                // mach was
            }

        };
    }

    var login_handlers = {
        200: function(data) {
            if(data.message == 'Logged In'){
                window.location.href = 'retrieving_charging_points';
            }
        },
        401: get_error_handler('{{ _("Invalid Login. Try again.") }}'),
        417: get_error_handler('{{ _("Oops! Something went wrong") }}')
    };

    return login_handlers;
} )();

frappe.ready(function() {
    login.bind_events();
    $(".for-login").toggle(true);
});