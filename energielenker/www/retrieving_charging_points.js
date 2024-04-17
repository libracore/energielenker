frappe.ready(function() {
    $(".retrieving").toggle(true);
    $(".success").toggle(false);
    $(".retrieving").on("submit", function(event){
        event.preventDefault();
        var qty = $("#evse_count").val();
        if (!qty) {
            show_error('Bitte geben Sie eine Anzahl an.')
            return false;
        } else if (isNaN(qty) || !Number.isInteger(parseFloat(qty))) {
            show_error("Bitte geben Sie eine ganze Zahl an.");
            return false;
        } else {
            validate_qty(qty);
        }
    });
});

function validate_qty(qty) {
    frappe.call({
        'method': 'energielenker.www.retrieving_charging_points.validate_qty',
        'args': {
            'qty_string': qty
        },
        'callback': function(response) {
            var validation = response.message;
            if (validation) {
                if (validation == "Error") {
                    show_error("Ein Fehler ist aufgetreten.");
                } else {
                    $("#license_key").val(validation);
                    console.log(qty);
                    $("#success_evse_count").text(qty);
                    $(".retrieving").toggle(false);
                    $(".success").toggle(true);
                }
            } else {
                show_error("Verfügbare Menge überschritten.");
            }
        }
    });
}

function show_error(error) {
    $("#form_error").html(`<i class="fa fa-exclamation-triangle" aria-hidden="true"></i> ${error}`);
    $("#form_error").show();
    $("#evse_count").css("border-color", "red");
}

