/*
Important(!)
Correct URL: /desk?depot=[depot_name]#depot-verarbeitung
Incorrect URL: /desk#depot-verarbeitung?depot=[depot_name]
*/

frappe.pages['depot-verarbeitung'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Depot Verarbeitung',
        single_column: true
    });

    page.main.html(frappe.render_template("depot", {}));

    page.query_parameter = frappe.depot.get_query_parameters();
    
    page.depot_fields = {};
    page.depot_fields.depot_field = frappe.depot.create_depot_field(page);
    page.depot_fields.project_field = frappe.depot.create_project_field(page);
    page.depot_fields.from_warehouse_field = frappe.depot.create_from_warehouse_field(page);
    page.depot_fields.to_warehouse_field = frappe.depot.create_to_warehouse_field(page);
    page.depot_fields.item_field = frappe.depot.create_item_field(page);
    page.depot_fields.aufbereiten_btn = frappe.depot.create_aufbereiten_btn(page);
    page.depot_fields.get_items_btn = frappe.depot.create_get_items_btn(page);

    frappe.depot.fetch_depot_data(page);

    setTimeout(function(){ page.depot_fields.item_field.set_focus(); }, 1000);
}

frappe.depot = {
    create_depot_field: function(page) {
        var depot_field = frappe.ui.form.make_control({
            parent: page.main.find(".depot_field"),
            df: {
                fieldtype: "Link",
                options: "Depot",
                fieldname: "depot",
                placeholder: "",
                read_only: 1,
                label: 'Depot'
            },
            only_input: false,
        });
        depot_field.set_value(page.query_parameter.depot || '');
        depot_field.refresh();
        return depot_field
    },
    create_project_field: function(page) {
        var project_field = frappe.ui.form.make_control({
            parent: page.main.find(".project_field"),
            df: {
                fieldtype: "Link",
                options: "Project",
                fieldname: "project",
                placeholder: "",
                read_only: 1,
                label: 'Project'
            },
            only_input: false,
        });

        project_field.refresh();
        return project_field
    },
    create_from_warehouse_field: function(page) {
        var from_warehouse_field = frappe.ui.form.make_control({
            parent: page.main.find(".from_warehouse_field"),
            df: {
                fieldtype: "Link",
                options: "Warehouse",
                fieldname: "from_warehouse",
                placeholder: "",
                read_only: 1,
                label: 'Ausgangslager'
            },
            only_input: false,
        });

        from_warehouse_field.refresh();
        return from_warehouse_field
    },
    create_to_warehouse_field: function(page) {
        var to_warehouse_field = frappe.ui.form.make_control({
            parent: page.main.find(".to_warehouse_field"),
            df: {
                fieldtype: "Link",
                options: "Warehouse",
                fieldname: "to_warehouse",
                placeholder: "",
                read_only: 1,
                label: 'Ziellager'
            },
            only_input: false,
        });

        to_warehouse_field.refresh();
        return to_warehouse_field
    },
    create_item_field: function(page) {
        var item_field = frappe.ui.form.make_control({
            parent: page.main.find(".item_field"),
            df: {
                fieldtype: "Text",
                options: "",
                fieldname: "items",
                placeholder: "",
                read_only: 0,
                label: "Artikel"
            },
            only_input: false,
        });
        item_field.refresh();
        return item_field
    },
    create_aufbereiten_btn: function(page) {
        var verarbeiten_btn = frappe.ui.form.make_control({
            parent: page.main.find(".aufbereiten_btn"),
            df: {
                fieldtype: "Button",
                options: "",
                fieldname: "aufbereiten",
                placeholder: "",
                read_only: 0,
                label: "Artikel aufbereiten",
                click: function() {
                    frappe.depot.strip_item_code(page);
                }
            },
            only_input: false
        });
        verarbeiten_btn.refresh();
        return verarbeiten_btn
    },
    create_get_items_btn: function(page) {
        var get_items_btn = frappe.ui.form.make_control({
            parent: page.main.find(".get_items_btn"),
            df: {
                fieldtype: "Button",
                options: "",
                fieldname: "get_items",
                placeholder: "",
                read_only: 0,
                label: "Get Items from Sales Order",
                click: function() {
                    frappe.depot.get_items_from_so(page);
                }
            },
            only_input: false
        });
        get_items_btn.refresh();
        return get_items_btn
    },
    create_verarbeiten_btn: function(page) {
        var verarbeiten_btn = frappe.ui.form.make_control({
            parent: page.main.find(".verarbeiten_btn"),
            df: {
                fieldtype: "Button",
                options: "",
                fieldname: "verarbeiten",
                placeholder: "",
                read_only: 1,
                label: "Artikel verarbeiten",
                click: function() {
                    frappe.depot.verarbeite_items(page)
                }
            },
            only_input: false
        });
        verarbeiten_btn.refresh();
        return verarbeiten_btn
    },
    get_query_parameters: function() {
        return (document.location.search).replace(/(^\?)/,'').split("&").map(function(n){return n = n.split("="),this[n[0]] = n[1],this}.bind({}))[0];
    },
    fetch_depot_data: function(page) {
        if (page.query_parameter.depot) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Depot",
                    name: page.query_parameter.depot,
                },
                callback(r) {
                    if(r.message) {
                        var depot = r.message;
                        page.depot_fields.project_field.set_value(depot.project);
                        page.depot_fields.project_field.refresh();
                        page.depot_fields.from_warehouse_field.set_value(depot.from_warehouse);
                        page.depot_fields.from_warehouse_field.refresh();
                        page.depot_fields.to_warehouse_field.set_value(depot.to_warehouse);
                        page.depot_fields.to_warehouse_field.refresh();
                    }
                }
            });
        }
    },
    strip_item_code: function(page) {
        page.depot_fields.aufbereiten_btn.hide();
        var item_codes = page.depot_fields.item_field.get_value();
        item_codes = item_codes
            .replaceAll("http://localhost:8000/desk#Form/Item/", "")
            .replaceAll("https://erp.energielenker.de/desk#Form/Item/", "")
            .replaceAll("https://erp-test.energielenker.de/desk#Form/Item/", "");
        frappe.depot.create_item_dict(page, item_codes);
    },
    create_item_dict: function(page, item_codes) {
        var found_items = [];
        var item_dict = {};
        for (var i = 0; i < item_codes.split("\n").length; i++) {
            if (found_items.includes(item_codes.split("\n")[i])) {
                item_dict[item_codes.split("\n")[i]] = item_dict[item_codes.split("\n")[i]] + 1
            } else {
                item_dict[item_codes.split("\n")[i]] = 1
                found_items.push(item_codes.split("\n")[i])
            }
        }
        var nice_json = JSON.stringify(item_dict)
            .replace("{", "{\n  ")
            .replaceAll('":', '": ')
            .replaceAll(',"', ',\n  "')
            .replaceAll('","', '",\n  "')
            .replace("}", "\n}")
        page.depot_fields.item_field.set_value(nice_json);
        page.depot_fields.item_field.refresh();
        page.depot_fields.verarbeiten_btn = frappe.depot.create_verarbeiten_btn(page);
    },
    get_items_from_so: function (page) {
        frappe.call({
            method: "energielenker.energielenker.page.depot_verarbeitung.depot_verarbeitung.make_so_material_transfer",
            args:{
                'depot': page.query_parameter.depot
            },
            freeze: true,
            freeze_message: 'Suche nach Artikel...',
            callback: function(r)
            {
                if (r.message) {
                    frappe.set_route("Form", "Stock Entry", r.message);
                }
            }
        });
    },
    verarbeite_items: function(page) {
        var item_dict = JSON.parse(page.depot_fields.item_field.get_value());
        frappe.call({
            method: "energielenker.energielenker.page.depot_verarbeitung.depot_verarbeitung.make_material_transfer",
            args:{
                'depot': page.query_parameter.depot,
                'items': item_dict
            },
            freeze: true,
            freeze_message: 'Suche nach Rechnungen...',
            callback: function(r)
            {
                if (r.message) {
                    frappe.set_route("Form", "Stock Entry", r.message);
                }
            }
        });
    }
}
