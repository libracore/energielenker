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
                            $("#timesheet_manager_stop").click(function(){
                                timesheet_manager_stop(data.timesheet.name);
                            });
                            $("#ts_indicator").addClass("pending-ts");
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
                timesheet_manager_stop(response.message);
            });
            $("#ts_indicator").addClass("pending-ts");
        }
    });
}

function timesheet_manager_start(ts) {
    frappe.prompt([
        {'fieldname': 'activity_type', 'fieldtype': 'Link', 'label': 'Activity Type', 'reqd': 1, 'options': 'Activity Type'},
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project'},
        {'fieldname': 'task', 'fieldtype': 'Link', 'label': 'Task', 'reqd': 0, 'options': 'Task'},
        {'fieldname': 'issue', 'fieldtype': 'Link', 'label': 'Issue', 'reqd': 0, 'options': 'Issue'},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0}
    ],
    function(values){
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

function timesheet_manager_add_timeblock(ts) {
    frappe.prompt([
        {'fieldname': 'hours', 'fieldtype': 'Float', 'label': 'Hours', 'reqd': 1},
        {'fieldname': 'activity_type', 'fieldtype': 'Link', 'label': 'Activity Type', 'reqd': 1, 'options': 'Activity Type'},
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project'},
        {'fieldname': 'task', 'fieldtype': 'Link', 'label': 'Task', 'reqd': 0, 'options': 'Task'},
        {'fieldname': 'issue', 'fieldtype': 'Link', 'label': 'Issue', 'reqd': 0, 'options': 'Issue'},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0}
    ],
    function(values){
        frappe.call({
            "method": "energielenker.energielenker.timesheet_manager.add_timeblock",
            "args": {
                    'ts': ts,
                    'details': values
                },
            "async": false,
            "callback": function(response) {}
        });
    },
    'Add Timeblock',
    'Add'
    )
}
