frappe.pages['vertriebs-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Vertriebs-Dashboard',
        single_column: true
    });
    
    var allow_user_filter = frappe.user.has_role("GL") ? true:false;
    if (allow_user_filter) {
        page.add_menu_item('Benutzer Filter', () => {
            frappe.el_vertriebsdashboard.benutzer_filter(page);
        });
        page.add_menu_item('Benutzer Farben Verwalten', () => {
            frappe.set_route('List', 'User Chart Color');
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
    let leads_chart = new energielenkerChart_vertrieb("Leads (Status Lead und Erstellt zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_leads', 'Lead', {'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    leads_chart.show();
    
    let open_quotation_qty_chart = new energielenkerChart_vertrieb("Anzahl offene Angebote (Dokumentenstatus Gebucht, Status Offen und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Open', 'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    open_quotation_qty_chart.show();
    
    let open_quotation_amount_chart = new energielenkerChart_vertrieb("Angebotsvolumen offener Angebote (Brutto, Dokumentenstatus Gebucht, Status Offen und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Open', 'qty': 0, 'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    open_quotation_amount_chart.show();
    
    let lost_quotation_qty_chart = new energielenkerChart_vertrieb("Anzahl verfallene Angebote (Dokumentenstatus Gebucht, Status Verloren und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Lost', 'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    lost_quotation_qty_chart.show();
    
    let lost_quotation_amount_chart = new energielenkerChart_vertrieb("Angebotsvolumen verfallener Angebote (Brutto, Dokumentenstatus Gebucht, Status Verloren und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Lost', 'qty': 0, 'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    lost_quotation_amount_chart.show();
    
    let sales_order_qty_chart = new energielenkerChart_vertrieb("Anzahl Aufträge (Dokumentenstatus Gebucht und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_sales_orders', 'Sales Order', {'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    sales_order_qty_chart.show();
    
    let sales_order_amount_chart = new energielenkerChart_vertrieb("Auftragssvolumen (Brutto, Dokumentenstatus Gebucht und Datum zwischen " + frappe.datetime.add_months(frappe.datetime.month_start(), -5) + " und " + frappe.datetime.month_end() + ")", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_sales_orders', 'Sales Order', {'qty': 0, 'user_filters': localStorage.getItem('user_filters') ? localStorage.getItem('user_filters'):false});
    sales_order_amount_chart.show();
    
    // reorder chart legend and resize chart height
    setTimeout(function(){ 
        // reorder chart legend
        var chart_legends = $(".chart-legend");
        chart_legends.each(function(){
           var versatz = 0;
           for (var i=1; i<=this.children.length; i++) {
               if (i % 2 == 0) {
                   $(this.children[i-1]).attr('transform', 'translate(' + versatz + ', 30)');
                   versatz = versatz + 105;
               } else {
                   $(this.children[i-1]).attr('transform', 'translate(' + versatz + ', 0)');
               }
           }
        });
        
        // resize chart height
        var charts = $(".frappe-chart.chart");
        charts.each(function(){
            $(this).attr('height', '270');
        });
        
        // resize chart hover
        var hovers = $(".data-point-list");
        hovers.each(function(){
            $(this).css('display', 'contents');
        });
    }, 2000);
}

class energielenkerChart_vertrieb {
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
                    if (frappe.user.has_role("GL")) {
                        if (this.document_type == 'Lead') {
                            frappe.route_options = {"status": 'Lead', "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                        } else if (this.document_type == 'Sales Order') {
                            frappe.route_options = {"docstatus": 1, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                        } else {
                            if (this.fetchFilter) {
                                frappe.route_options = {"status": this.fetchFilter.quotation_status, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                            }
                        }
                    } else {
                        if (this.document_type == 'Lead') {
                            frappe.route_options = {"status": 'Lead', "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], "lead_owner": frappe.session.user}
                        } else if (this.document_type == 'Sales Order') {
                            frappe.route_options = {"docstatus": 1, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], "ansprechpartner": frappe.session.user}
                        } else {
                            if (this.fetchFilter) {
                                frappe.route_options = {"status": this.fetchFilter.quotation_status, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], "ansprechpartner": frappe.session.user}
                            }
                        }
                    }
                    frappe.set_route('List', this.document_type);
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
            stacked: frappe.user.has_role("GL") ? true:false,
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

frappe.el_vertriebsdashboard = {
    benutzer_filter: function(page) {
        var d = new frappe.ui.Dialog({
            'title': __('Benutzer Filter'),
            'fields': [
                {'fieldname': 'user', 'fieldtype': 'Link', 'options': 'User', 'label': 'Benutzer', 'reqd': 0,
                    'change': function() {
                        if (d.get_value('user')) {
                            if (d.get_value('user_list')) {
                                d.set_value('user_list', d.get_value('user_list') + "\n" + d.get_value('user'));
                            } else {
                                d.set_value('user_list', d.get_value('user'));
                            }
                            d.set_value('user', '')
                        }
                    }
                },
                {'fieldname': 'user_list', 'fieldtype': 'Code', 'label': 'Anzuzeigende Benutzer', 'reqd': 0, 'description': 'Pro Zeile ein Benutzer. Zum Entfernen die entsprechende Zeile entfernen.',
                    'default': localStorage.getItem('user_filters') ? frappe.el_vertriebsdashboard.get_benutzer_filter():''
                },
                {'fieldname': 'remove_filter', 'fieldtype': 'Button', 'label': 'Alle Benutzer entfernen', 'reqd': 0,
                    'click': function() {
                        d.set_value('user_list', '');
                    }
                }
            ],
            primary_action: function(){
                var users_from_list = d.get_value('user_list').split("\n");
                localStorage.setItem('user_filters', users_from_list);
                
                d.hide();
                window.location.reload();
            },
            primary_action_label: __('Filter Anwenden')
        });
        d.show();
    },
    get_benutzer_filter: function(){
        var user_filters = localStorage.getItem('user_filters').split(",");
        var user_filter_txt = '';
        for (var i = 0; i<user_filters.length; i++) {
            if (i==0) {
                user_filter_txt = user_filters[i];
            } else {
                user_filter_txt = user_filter_txt + "\n" + user_filters[i];
            }
        }
        return user_filter_txt
    }
}
