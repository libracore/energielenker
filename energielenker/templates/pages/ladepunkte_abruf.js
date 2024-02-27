$(document).ready(function(){
    make();
    run();
});


function make() {
    
}

function run() {
    //start process when button has been pushed
    $(".btn-submit").on('click', function() {
		var call = [];
		var dict = {};
		dict['set_size'] = document.getElementById('set').value;
		dict['quantity'] = document.getElementById('quantity').value;
		call.push(dict);
		var customer = document.getElementById('customer').value;
        frappe.call({
            'method': 'energielenker.templates.pages.ladepunkte_abruf.call_ladepunkte',
            'args': {
                'call': call,
                'customer': customer
            },
            'callback': function(r) {
                console.log("Hallo");
            }
        });
	});
}
