$(document).ready(function(){
    setTimeout(function(){
        frappe.call({
            "method": "energielenker.energielenker.timesheet_manager.get_data",
            "args": {},
            "async": false,
            "callback": function(response) {
                var data = response.message;
                $('.nav.navbar-nav.navbar-right').prepend(frappe.render_template("ts_navbar", data));
                if (data.employee != 0) {
                    if (data.timesheet != 0) {
                        if (data.timer_status == 'stopped') {
                            $("#timesheet_manager_start").click(function(){
                                timesheet_manager_start(data.timesheet.name);
                            });
                            $("#timesheet_manager_quick_start").click(function(){
                                timesheet_manager_quick_start(data.timesheet.name);
                            });
                            $("#timesheet_manager_add_timeblock").click(function(){
                                timesheet_manager_add_timeblock(data.timesheet.name);
                            });
                        } else {
                            if (data.timer_status == 'quick_entry') {
                                $("#timesheet_manager_stop").click(function(){
                                    timesheet_manager_stop_from_quick_entry(data.timesheet.name);
                                });
                                $("#ts_indicator").addClass("pending-ts");
                            } else {
                                $("#timesheet_manager_stop").click(function(){
                                    timesheet_manager_stop(data.timesheet.name);
                                });
                                $("#ts_indicator").addClass("pending-ts");
                            }
                        }
                    } else {
                        $("#timesheet_manager_start").click(function(){
                            timesheet_manager_start('new');
                        });
                        $("#timesheet_manager_quick_start").click(function(){
                            timesheet_manager_quick_start('new');
                        });
                        $("#timesheet_manager_add_timeblock").click(function(){
                            timesheet_manager_add_timeblock('new');
                        });
                    }
                }
            }
        });
        
        // mark navbar of test system red
        var navbars = document.getElementsByClassName("navbar");
        if (navbars.length > 0) {
            if ((window.location.hostname.includes("erp-test"))) {
                navbars[0].style.backgroundColor = "#d68080";
            }
        }
    }, 1000);
});

function timesheet_manager_quick_start(ts) {
    frappe.call({
        "method": "energielenker.energielenker.timesheet_manager.quick_start_timer",
        "args": {
                'ts': ts
            },
        "async": false,
        "callback": function(response) {
            // remove start-buttons, add stop-button
            $("#timesheet_manager_start").remove();
            $("#timesheet_manager_quick_start").remove();
            $("#timesheet_manager_add_timeblock").remove();
            $("#timesheet_manager").append('<button type="button" id="timesheet_manager_stop" class="btn btn-danger timesheet-manager-stop">' + __("Stop Timer") + '</button>');
            $("#timesheet_manager_stop").click(function(){
                timesheet_manager_stop_from_quick_entry(response.message);
            });
            $("#ts_indicator").addClass("pending-ts");
        }
    });
}

function timesheet_manager_start(ts) {
    frappe.prompt([
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project'},
        {'fieldname': 'task', 'fieldtype': 'Link', 'label': 'Task', 'reqd': 0, 'options': 'Task',
            'get_query': function() {
                if ($('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value) {
                    return { 'filters': { 'project': $('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value } };
                } else {
                    return {}
                }
            }
        },
        {'fieldname': 'issue', 'fieldtype': 'Link', 'label': 'Issue', 'reqd': 0, 'options': 'Issue',
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
        {'fieldname': 'tbd', 'fieldtype': 'Check', 'label': 'Noch zu klären', 'reqd': 0, 'default': 0},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 0, 'default': ''}
    ],
    function(values){
        if (!values.issue && !values.task) {
            frappe.msgprint( __("Please set a task or issue"), __("Validation") );
        } else {
            frappe.call({
                "method": "energielenker.energielenker.timesheet_manager.start_timer",
                "args": {
                        'ts': ts,
                        'details': values
                    },
                "async": false,
                "callback": function(response) {
                    // remove start-buttons, add stop-button
                    $("#timesheet_manager_start").remove();
                    $("#timesheet_manager_quick_start").remove();
                    $("#timesheet_manager_add_timeblock").remove();
                    $("#timesheet_manager").append('<button type="button" id="timesheet_manager_stop" class="btn btn-danger timesheet-manager-stop">' + __("Stop Timer") + '</button>');
                    $("#timesheet_manager_stop").click(function(){
                        timesheet_manager_stop(response.message);
                    });
                    $("#ts_indicator").addClass("pending-ts");
                }
            });
        }
    },
    'Timelog Detail',
    'Start'
    )
}

function timesheet_manager_stop(ts) {
    frappe.call({
        "method": "energielenker.energielenker.timesheet_manager.stop_timer",
        "args": {
                'ts': ts
            },
        "async": false,
        "callback": function(response) {
            // remove stop-button, add start-buttons
            $("#timesheet_manager_stop").remove();
            $("#timesheet_manager").append('<button type="button" id="timesheet_manager_quick_start" class="btn btn-success timesheet-manager-start">' + __("Quick Start Timer") + '</button>');
            $("#timesheet_manager").append('<button type="button" id="timesheet_manager_start" class="btn btn-success timesheet-manager-start">' + __("Start Timer") + '</button>');
            $("#timesheet_manager").append('<button type="button" id="timesheet_manager_add_timeblock" class="btn btn-warning timesheet-manager-start">' + __("Add Timeblock") + '</button>');
            $("#timesheet_manager_start").click(function(){
                timesheet_manager_start(response.message);
            });
            $("#timesheet_manager_quick_start").click(function(){
                timesheet_manager_quick_start(response.message);
            });
            
            $("#timesheet_manager_add_timeblock").click(function(){
                timesheet_manager_add_timeblock(response.message);
            });
            $("#ts_indicator").removeClass("pending-ts");
        }
    });
}

function timesheet_manager_stop_from_quick_entry(ts) {
    frappe.prompt([
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project'},
        {'fieldname': 'task', 'fieldtype': 'Link', 'label': 'Task', 'reqd': 0, 'options': 'Task',
            'get_query': function() {
                if ($('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value) {
                    return { 'filters': { 'project': $('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value } };
                } else {
                    return {}
                }
            }
        },
        {'fieldname': 'issue', 'fieldtype': 'Link', 'label': 'Issue', 'reqd': 0, 'options': 'Issue',
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
        {'fieldname': 'tbd', 'fieldtype': 'Check', 'label': 'Noch zu klären', 'reqd': 0, 'default': 0},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 0, 'default': ''}
    ],
    function(values){
        if (!values.issue && !values.task) {
            frappe.msgprint( __("Please set a task or issue"), __("Validation") );
        } else {
            frappe.call({
                "method": "energielenker.energielenker.timesheet_manager.stop_timer_from_quick_start",
                "args": {
                        'ts': ts,
                        'details': values
                    },
                "async": false,
                "callback": function(response) {
                    // remove stop-button, add start-buttons
                    $("#timesheet_manager_stop").remove();
                    $("#timesheet_manager").append('<button type="button" id="timesheet_manager_quick_start" class="btn btn-success timesheet-manager-start">' + __("Quick Start Timer") + '</button>');
                    $("#timesheet_manager").append('<button type="button" id="timesheet_manager_start" class="btn btn-success timesheet-manager-start">' + __("Start Timer") + '</button>');
                    $("#timesheet_manager").append('<button type="button" id="timesheet_manager_add_timeblock" class="btn btn-warning timesheet-manager-start">' + __("Add Timeblock") + '</button>');
                    $("#timesheet_manager_start").click(function(){
                        timesheet_manager_start(response.message);
                    });
                    $("#timesheet_manager_quick_start").click(function(){
                        timesheet_manager_quick_start(response.message);
                    });
                    
                    $("#timesheet_manager_add_timeblock").click(function(){
                        timesheet_manager_add_timeblock(response.message);
                    });
                    $("#ts_indicator").removeClass("pending-ts");
                }
            });
        }
    },
    'Timelog Detail',
    'Stop'
    )
}

function timesheet_manager_add_timeblock(ts) {
    frappe.prompt([
        {'fieldname': 'hours', 'fieldtype': 'Float', 'label': 'Hours', 'reqd': 1},
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project'},
        {'fieldname': 'task', 'fieldtype': 'Link', 'label': 'Task', 'reqd': 0, 'options': 'Task',
            'get_query': function() {
                if ($('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value) {
                    return { 'filters': { 'project': $('[data-fieldname="project"]')[$('[data-fieldname="project"]').length - 1].value } };
                } else {
                    return {}
                }
            }
        },
        {'fieldname': 'issue', 'fieldtype': 'Link', 'label': 'Issue', 'reqd': 0, 'options': 'Issue',
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
        {'fieldname': 'tbd', 'fieldtype': 'Check', 'label': 'Noch zu klären', 'reqd': 0, 'default': 0},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 0, 'default': ''}
    ],
    function(values){
        if (!values.issue && !values.task) {
            frappe.msgprint( __("Please set a task or issue"), __("Validation") );
        } else {
            frappe.call({
                "method": "energielenker.energielenker.timesheet_manager.add_timeblock",
                "args": {
                        'ts': ts,
                        'details': values
                    },
                "async": false,
                "callback": function(response) {}
            });
        }
    },
    'Add Timeblock',
    'Add'
    )
}
