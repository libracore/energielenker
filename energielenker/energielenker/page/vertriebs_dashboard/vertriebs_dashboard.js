frappe.pages['vertriebs-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Vertriebs-Dashboard',
        single_column: true
    });
    
    // create chart area
    var chartWrapper = $(wrapper);
    $(`<div class="dashboard">
            <div class="dashboard-graph row"></div>
        </div>`).appendTo(chartWrapper.find(".page-content").empty());
    var chartContainer = chartWrapper.find(".dashboard-graph");
    
    // create charts
    let leads_chart = new energielenkerChart("Leads", chartContainer, 'Full', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_leads', 'Lead', {});
    leads_chart.show();
    
    let open_quotation_qty_chart = new energielenkerChart("Anzahl offene Angebote", chartContainer, 'Half', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Open'});
    open_quotation_qty_chart.show();
    
    let open_quotation_amount_chart = new energielenkerChart("Angebotsvolumen offener Angebote", chartContainer, 'Half', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Open', 'qty': 0});
    open_quotation_amount_chart.show();
    
    let lost_quotation_qty_chart = new energielenkerChart("Anzahl verfallene Angebote", chartContainer, 'Half', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Lost'});
    lost_quotation_qty_chart.show();
    
    let lost_quotation_amount_chart = new energielenkerChart("Angebotsvolumen verfallener Angebote", chartContainer, 'Half', 'Bar', 'energielenker.energielenker.page.vertriebs_dashboard.vertriebs_dashboard.get_quotations', 'Quotation', {'quotation_status': 'Lost', 'qty': 0});
    lost_quotation_amount_chart.show();
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
            this.data = data;
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
                        } else {
                            if (this.fetchFilter) {
                                frappe.route_options = {"status": this.fetchFilter.quotation_status, "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]]}
                            }
                        }
                    } else {
                        if (this.document_type == 'Lead') {
                            frappe.route_options = {"status": 'Lead', "creation": ['between', [frappe.datetime.add_months(frappe.datetime.month_start(), -5), frappe.datetime.month_end()]], "lead_owner": frappe.session.user}
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
            colors: ["light-blue"],
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
