frappe.ready(function() {
    $(".retrieving").toggle(true);
    $("#create_license_key").click(function(){
        var qty = $("#evse_count");
        console.log(qty);
        validate_qty(qty);
    });
});

function validate_qty(qty) {
    frappe.call({
        'method': 'energielenker.www.retrieving_charging_points.validate_qty',
        'args': {
            'qty': qty
        },
        'callback': function(response) {
            console.log(response.message);
            var validation = response.message;
            if (validation) {
                console.log("shit");
                window.location.href = 'charging_points_success';
            } else {
                console.log("peace");
                $("#qty_error").show();
            }
        }
    });
}
