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
    }).then((login_status) => {
        if (['User disabled or missing', 'Incorrect password'].includes(login_status['message'])) {
            $("#login_error").show();
        } else if (login_status['full_name']) {
            window.location.href = 'retrieving_charging_points';
        } else {
            $("#login_error").show();
        }
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
                $("#login_error").show();
            } else {
                // mach was??
            }

        };
    }

    var login_handlers = {
        200: function(data) {
            if(data.message == 'Logged In'){
                window.location.href = 'retrieving_charging_points';
            }
        },
        401: get_error_handler('{{ _("Invalid Login. Try again.") }}')
    };

    return login_handlers;
} )();

frappe.ready(function() {
    login.bind_events();
    $(".for-login").toggle(true);
});

function forgot_password() {
    window.location.href = '/forgot_password_webshop';
}

function back_to_login() {
    window.location.href = '/webshop_login';
}

//forgot password
	$(".form-forgot").on("submit", function(event) {
		event.preventDefault();
		var args = {};
		args.cmd = "energielenker.www.webshop_login.reset_webshop_password";
		args.user = ($("#forgot_password_email").val() || "").trim();
        args.send_email = true
		if(!args.user) {
            console.log("tschau");
			//~ login.set_indicator('{{ _("Valid Login id required.") }}', 'red');
			return false;
		}
		login.call(args);
        //~ was machi da weni uf return zuegriffe will?
		return false;
	});
    
// Login
login.call = function(args, callback) {
	//~ login.set_indicator('{{ _("Verifying...") }}', 'blue');

	return frappe.call({
		type: "POST",
		args: args,
		callback: callback,
		freeze: true,
		statusCode: login.login_handlers
	});
}
