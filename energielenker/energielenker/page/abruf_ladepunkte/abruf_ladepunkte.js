frappe.pages['abruf-ladepunkte'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Abruf Ladepunkte',
		single_column: true
	});
}

$(document).ready(function(){
    make();
    run();
});

function make() {
    page.main.html(frappe.render_template("abruf_ladepunkte", {}));
    page.set_primary_action('Daten Laden', () => {
        console.log("Hoi");
    });
}




