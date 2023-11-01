frappe.pages['controlling-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Controlling-Dashboard',
        single_column: true
    });
    
    var allow_user_filter = frappe.user.has_role("GL") ? true:false;
    if (allow_user_filter) {
        page.add_menu_item('Profit-Center- und Lager-Filter', () => {
            frappe.el_controllingdashboard.benutzer_filter(page);
        });
        page.add_menu_item('Profit-Center Farben Verwalten', () => {
            frappe.set_route('List', 'Cost Center');
        });
        page.add_menu_item('Lager Farben Verwalten', () => {
            frappe.set_route('List', 'Warehouse');
        });
    }
    
    $("body").addClass("full-width");
    
    // create chart area
    var chartWrapper = $(wrapper);
    $(`<div class="dashboard">
            <div class="dashboard-graph row"></div>
        </div>`).appendTo(chartWrapper.find(".page-content").empty());
    var chartContainer = chartWrapper.find(".dashboard-graph");
    
    // create charts
    let auftragsvolumen_chart = new energielenkerChart("Auftragsvolumen (Brutto, Dokumentenstatus Gebucht und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.controlling_dashboard.controlling_dashboard.get_auftragsvolumen', 'Sales Order', {'pc_filters': localStorage.getItem('cost_center_filters') ? localStorage.getItem('cost_center_filters'):false});
    auftragsvolumen_chart.show();
    let angebotsvolumen_chart = new energielenkerChart("Angebotsvolumen (Brutto, Dokumentenstatus Gebucht, Status weder Verloren noch Bestellt und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.controlling_dashboard.controlling_dashboard.get_angebotsvolumen', 'Quotation', {'pc_filters': localStorage.getItem('cost_center_filters') ? localStorage.getItem('cost_center_filters'):false});
    angebotsvolumen_chart.show();
    let ausgangsrechnung_chart = new energielenkerChart("Ausgangsrechnungen (Brutto, Dokumentenstatus Gebucht und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.controlling_dashboard.controlling_dashboard.get_ausgangsrechnungen', 'Sales Invoice', {'pc_filters': localStorage.getItem('cost_center_filters') ? localStorage.getItem('cost_center_filters'):false});
    ausgangsrechnung_chart.show();
    let eingangsrechnungen_chart = new energielenkerChart("Eingangsrechnungen (Brutto, Dokumentenstatus Gebucht und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.controlling_dashboard.controlling_dashboard.get_eingangsrechnungen', 'Purchase Invoice', {'pc_filters': localStorage.getItem('cost_center_filters') ? localStorage.getItem('cost_center_filters'):false, 'warehouse_filters': localStorage.getItem('warehouse_filters') ? localStorage.getItem('warehouse_filters'):false});
    eingangsrechnungen_chart.show();
    let lagerwert = new energielenkerChart("Lagerwert (Per Ende des Monats)", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.controlling_dashboard.controlling_dashboard.get_lagerwert', 'General Ledger', {});
    lagerwert.show();
}

class energielenkerChart {
    constructor(chart_name, chart_container, chartWidth, chartType, fetchMethod, document_type, fetchFilter) {
        this.container = chart_container;
        this.chart_name = chart_name;
        this.chartType = chartType;
        this.fetchMethod = fetchMethod;
        this.chartWidth = chartWidth;
        this.document_type = document_type;
        this.fetchFilter = fetchFilter||{}
    }

    show() {
        this.prepare_container();
        this.prepare_chart_actions();
        this.fetch().then((data) => {
            this.data = data.dataset;
            this.colors = data.colors;
            this.render();
        });
    }

    prepare_container() {
        const column_width_map = {
            "Half": "6",
            "Full": "12",
        };
        let columns = column_width_map[this.chartWidth];
        this.chart_container = $(`<div class="col-sm-${columns} chart-column-container">
            <div class="chart-wrapper">
                <div class="chart-name-placeholder hide text-muted">${this.chart_name}</div>
                <div class="chart-loading-state text-muted">${__("Loading...")}</div>
                <div class="chart-empty-state hide text-muted">${__("No Data")}</div>
            </div>
        </div>`);
        this.chart_container.appendTo(this.container);
    }

    prepare_chart_actions() {
        if (this.document_type) {
            let actions = [{
                label: __("{0} List", [this.document_type]),
                action: 'action-list',
                handler: () => {
                    if (this.document_type == 'Sales Order') {
                        frappe.route_options = {"docstatus": 1, "transaction_date": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                    } else if (this.document_type == 'Quotation') {
                        frappe.route_options = {"docstatus": 1, "transaction_date": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], 'status': ['not in', ['Lost', 'Ordered']]}
                    } else if (this.document_type == 'Sales Invoice') {
                        frappe.route_options = {"docstatus": 1, "posting_date": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                    } else if (this.document_type == 'Purchase Invoice') {
                        frappe.route_options = {"docstatus": 1, "posting_date": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                    } else if (this.document_type == 'General Ledger') {
                        frappe.route_options = {"from_date": frappe.datetime.add_months(frappe.datetime.month_start(), -5), "to_date": frappe.datetime.month_end(), "account": '1000 - Roh-, Hilfs- und Betriebsstoffe (Bestand) - S'}
                        frappe.set_route('query-report', this.document_type);
                    } else {
                        if (this.fetchFilter) {
                            frappe.route_options = {"status": this.fetchFilter.quotation_status, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], "ansprechpartner": frappe.session.user}
                        }
                    }
                    if (this.document_type != 'General Ledger') {
                        frappe.set_route('List', this.document_type);
                    }
                }
            }]
            this.set_chart_actions(actions);
        }
    }

    set_chart_actions(actions) {
        this.chart_actions = $(`<div class="chart-actions btn-group dropdown pull-right" style="z-index: 1000;">
            <a class="dropdown-toggle" data-toggle="dropdown"
                aria-haspopup="true" aria-expanded="false"> <button class="btn btn-default btn-xs"><span class="caret"></span></button>
            </a>
            <ul class="dropdown-menu" style="max-height: 300px; overflow-y: auto;">
                ${actions.map(action => `<li><a data-action="${action.action}">${action.label}</a></li>`).join('')}
            </ul>
        </div>
        `);

        this.chart_actions.find("a[data-action]").each((i, o) => {
            const action = o.dataset.action;
            $(o).click(actions.find(a => a.action === action));
        });
        this.chart_actions.prependTo(this.chart_container);
    }

    fetch(refresh=false) {
        this.chart_container.find('.chart-loading-state').removeClass('hide');
        let method = this.fetchMethod;
        let filter = this.fetchFilter;
        return frappe.xcall(
            method,
            filter
        );
    }

    render() {
        const chart_type_map = {
            "Line": "line",
            "Bar": "bar",
        };
        
        const bar_options = {
            stacked: true,
            spaceRatio: 0.5
        };
        
        let chart_args = {
            title: this.chart_name,
            data: this.data,
            type: chart_type_map[this.chartType],
            truncateLegends: 1,
            colors: this.colors ? this.colors:["light-blue"],
            axisOptions: {
                xIsSeries: 0,
                shortenYAxisNumbers: 1
            },
            barOptions: bar_options
        };
        
        if(!this.chart) {
            this.chart = new frappe.Chart(this.chart_container.find(".chart-wrapper")[0], chart_args);
        }
    }
}

frappe.el_controllingdashboard = {
    benutzer_filter: function(page) {
        var d = new frappe.ui.Dialog({
            'title': __('Profit-Center Filter'),
            'fields': [
                {'fieldname': 'cost_center', 'fieldtype': 'Link', 'options': 'Cost Center', 'label': 'Profit-Center', 'reqd': 0,
                    'change': function() {
                        if (d.get_value('cost_center')) {
                            frappe.db.get_value("Cost Center", d.get_value('cost_center'), 'cost_center_number').then((data) => {
                                cost_center_number = data.message.cost_center_number;
                                if (d.get_value('cost_center_list')) {
                                    d.set_value('cost_center_list', d.get_value('cost_center_list') + "\n" + cost_center_number);
                                } else {
                                    d.set_value('cost_center_list', cost_center_number);
                                }
                                d.set_value('cost_center', '')
                            });
                        }
                    }
                },
                {'fieldname': 'cost_center_list', 'fieldtype': 'Code', 'label': 'Anzuzeigende Profit-Center', 'reqd': 0, 'description': 'Pro Zeile ein Profit-Center. Zum Entfernen die entsprechende Zeile entfernen.',
                    'default': localStorage.getItem('cost_center_filters') ? frappe.el_controllingdashboard.get_cost_center_filters():''
                },
                {'fieldname': 'remove_filter', 'fieldtype': 'Button', 'label': 'Alle Profit-Center entfernen', 'reqd': 0,
                    'click': function() {
                        d.set_value('cost_center_list', '');
                    }
                },
                {'fieldname': 'warehouse', 'fieldtype': 'Link', 'options': 'Warehouse', 'label': 'Lager', 'reqd': 0, 'description': 'Wird nur bei den Eingangsrechnungen angewendet',
                    'change': function() {
                        if (d.get_value('warehouse')) {
                            if (d.get_value('warehouse_list')) {
                                d.set_value('warehouse_list', d.get_value('warehouse_list') + "\n" + d.get_value('warehouse'));
                            } else {
                                d.set_value('warehouse_list', d.get_value('warehouse'));
                            }
                            d.set_value('warehouse', '')
                        }
                    }
                },
                {'fieldname': 'warehouse_list', 'fieldtype': 'Code', 'label': 'Anzuzeigende Lager', 'reqd': 0, 'description': 'Pro Zeile ein Lager. Zum Entfernen die entsprechende Zeile entfernen.',
                    'default': localStorage.getItem('warehouse_filters') ? frappe.el_controllingdashboard.get_warehouse_filters():''
                },
                {'fieldname': 'remove_warehouse_filter', 'fieldtype': 'Button', 'label': 'Alle Lager entfernen', 'reqd': 0,
                    'click': function() {
                        d.set_value('warehouse_list', '');
                    }
                }
            ],
            primary_action: function(){
                var cost_centers_from_list = d.get_value('cost_center_list').split("\n");
                localStorage.setItem('cost_center_filters', cost_centers_from_list);
                var warehouses_from_list = d.get_value('warehouse_list').split("\n");
                localStorage.setItem('warehouse_filters', warehouses_from_list);
                
                d.hide();
                window.location.reload();
            },
            primary_action_label: __('Filter Anwenden')
        });
        d.show();
    },
    get_cost_center_filters: function(){
        var cost_center_filters = localStorage.getItem('cost_center_filters').split(",");
        var cost_center_filters_txt = '';
        for (var i = 0; i<cost_center_filters.length; i++) {
            if (i==0) {
                cost_center_filters_txt = cost_center_filters[i];
            } else {
                cost_center_filters_txt = cost_center_filters_txt + "\n" + cost_center_filters[i];
            }
        }
        return cost_center_filters_txt
    },
    get_warehouse_filters: function(){
        var warehouse_filters = localStorage.getItem('warehouse_filters').split(",");
        var warehouse_filters_txt = '';
        for (var i = 0; i<warehouse_filters.length; i++) {
            if (i==0) {
                warehouse_filters_txt = warehouse_filters[i];
            } else {
                warehouse_filters_txt = warehouse_filters_txt + "\n" + warehouse_filters[i];
            }
        }
        return warehouse_filters_txt
    }
}
