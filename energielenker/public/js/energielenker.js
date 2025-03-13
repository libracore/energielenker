frappe.provide("frappe.model");

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

$(window).on('hashchange', function() {
    // redirect from #query-report/Stock Ledger
    if(frappe._cur_route=="#query-report/Stock%20Ledger") {
        window.location.href = "#query-report/energielenker%20Lagerbuch";
    }
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
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project', 
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
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
        {'fieldname': 'typisierung', 'fieldtype': 'Select', 'label': 'Typisierung', 'reqd': 1, 'options': 'Projekt\nSupport gem. Rahmenvertrag\nRufbereitschaft\nsonstiger Support'},
        {'fieldname': 'rufbereitschaft_von', 'fieldtype': 'Time', 'label': 'Von', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'rufbereitschaft_bis', 'fieldtype': 'Time', 'label': 'Bis', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 1}
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
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project',
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
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
        {'fieldname': 'typisierung', 'fieldtype': 'Select', 'label': 'Typisierung', 'reqd': 1, 'options': 'Projekt\nSupport gem. Rahmenvertrag\nRufbereitschaft\nsonstiger Support'},
        {'fieldname': 'rufbereitschaft_von', 'fieldtype': 'Time', 'label': 'Von', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'rufbereitschaft_bis', 'fieldtype': 'Time', 'label': 'Bis', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 1}
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
        {'fieldname': 'project', 'fieldtype': 'Link', 'label': 'Project', 'reqd': 0, 'options': 'Project',
            'get_query': function() {
                return { 'filters': { 'status': 'Open' } };
            }
        },
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
        {'fieldname': 'typisierung', 'fieldtype': 'Select', 'label': 'Typisierung', 'reqd': 1, 'options': 'Projekt\nSupport gem. Rahmenvertrag\nRufbereitschaft\nsonstiger Support'},
        {'fieldname': 'rufbereitschaft_von', 'fieldtype': 'Time', 'label': 'Von', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'rufbereitschaft_bis', 'fieldtype': 'Time', 'label': 'Bis', 'reqd': 0, 'depends_on': "eval:doc.typisierung=='Rufbereitschaft'"},
        {'fieldname': 'bill', 'fieldtype': 'Check', 'label': 'Bill', 'reqd': 0, 'default': 0},
        {'fieldname': 'remarks', 'fieldtype': 'Small Text', 'label': __('Remarks'), 'reqd': 1}
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

$.extend(frappe.model, {
	new_names: {},
	new_name_count: {},

	get_new_doc: function(doctype, parent_doc, parentfield, with_mandatory_children) {
		frappe.provide("locals." + doctype);
		var doc = {
			docstatus: 0,
			doctype: doctype,
			name: frappe.model.get_new_name(doctype),
			__islocal: 1,
			__unsaved: 1,
			owner: frappe.session.user
		};
		frappe.model.set_default_values(doc, parent_doc);

		if(parent_doc) {
			$.extend(doc, {
				parent: parent_doc.name,
				parentfield: parentfield,
				parenttype: parent_doc.doctype,
			});
			if(!parent_doc[parentfield]) parent_doc[parentfield] = [];
			doc.idx = parent_doc[parentfield].length + 1;
			parent_doc[parentfield].push(doc);
		} else {
			frappe.provide("frappe.model.docinfo." + doctype + "." + doc.name);
		}

		frappe.model.add_to_locals(doc);

		if(with_mandatory_children) {
			frappe.model.create_mandatory_children(doc);
		}

		if (!parent_doc) {
			doc.__run_link_triggers = 1;
		}

		// set the name if called from a link field
		if(frappe.route_options && frappe.route_options.name_field) {

			var meta = frappe.get_meta(doctype);
			// set title field / name as name
			if(meta.autoname && meta.autoname.indexOf("field:")!==-1) {
				doc[meta.autoname.substr(6)] = frappe.route_options.name_field;
			} else if(meta.title_field) {
				doc[meta.title_field] = frappe.route_options.name_field;
			}


			delete frappe.route_options.name_field;
		}

		// set route options
		if(frappe.route_options && !doc.parent) {
			$.each(frappe.route_options, function(fieldname, value) {
				var df = frappe.meta.has_field(doctype, fieldname);
				if(df && in_list(['Link', 'Data', 'Select', 'Dynamic Link'], df.fieldtype) && !df.no_copy) {
					doc[fieldname]=value;
				}
			});
			frappe.route_options = null;
		}

		return doc;
	},

	make_new_doc_and_get_name: function(doctype, with_mandatory_children) {
		return frappe.model.get_new_doc(doctype, null, null, with_mandatory_children).name;
	},

	get_new_name: function(doctype) {
		var cnt = frappe.model.new_name_count
		if(!cnt[doctype])
			cnt[doctype] = 0;
		cnt[doctype]++;
		return __('New') + ' '+ __(doctype) + ' ' + cnt[doctype];
	},

	set_default_values: function(doc, parent_doc) {
		var doctype = doc.doctype;
		var docfields = frappe.meta.get_docfields(doctype);
		var updated = [];
		for(var fid=0;fid<docfields.length;fid++) {
			var f = docfields[fid];
			if(!in_list(frappe.model.no_value_type, f.fieldtype) && doc[f.fieldname]==null) {
				var v = frappe.model.get_default_value(f, doc, parent_doc);
				if(v) {
					if(in_list(["Int", "Check"], f.fieldtype))
						v = cint(v);
					else if(in_list(["Currency", "Float"], f.fieldtype))
						v = flt(v);

					doc[f.fieldname] = v;
					updated.push(f.fieldname);
				} else if(f.fieldtype == "Select" && f.options && typeof f.options === 'string'
					&& !in_list(["[Select]", "Loading..."], f.options)) {

					doc[f.fieldname] = f.options.split("\n")[0];
				}
			}
		}
		return updated;
	},

	create_mandatory_children: function(doc) {
		var meta = frappe.get_meta(doc.doctype);
		if(meta && meta.istable) return;

		// create empty rows for mandatory table fields
		frappe.meta.get_docfields(doc.doctype).forEach(function(df) {
			if(df.fieldtype==='Table' && df.reqd) {
				frappe.model.add_child(doc, df.fieldname);
			}
		});
	},

	get_default_value: function(df, doc, parent_doc) {
		var user_default = "";
		var user_permissions = frappe.defaults.get_user_permissions();
		let allowed_records = [];
		let default_doc = null;
		if(user_permissions) {
			({allowed_records, default_doc} = frappe.perm.filter_allowed_docs_for_doctype(user_permissions[df.options], doc.doctype));
		}
		var meta = frappe.get_meta(doc.doctype);
		var has_user_permissions = (df.fieldtype==="Link"
			&& !$.isEmptyObject(user_permissions)
			&& df.ignore_user_permissions != 1
			&& allowed_records.length);

		// don't set defaults for "User" link field using User Permissions!
		if (df.fieldtype==="Link" && df.options!=="User") {
			// 1 - look in user permissions for document_type=="Setup".
			// We don't want to include permissions of transactions to be used for defaults.
			if (df.linked_document_type==="Setup"
				&& has_user_permissions && default_doc) {
				return default_doc;
			}

			if(!df.ignore_user_permissions) {
				// 2 - look in user defaults
				var user_defaults = frappe.defaults.get_user_defaults(df.options);
				if (user_defaults && user_defaults.length===1) {
					// Use User Permission value when only when it has a single value
					user_default = user_defaults[0];
				}
			}

			if (!user_default) {
				user_default = frappe.defaults.get_user_default(df.fieldname);
			}

			if(!user_default && df.remember_last_selected_value && frappe.boot.user.last_selected_values) {
				user_default = frappe.boot.user.last_selected_values[df.options];
			}

			var is_allowed_user_default = user_default &&
				(!has_user_permissions || allowed_records.includes(user_default));

			// is this user default also allowed as per user permissions?
			if (is_allowed_user_default) {
				return user_default;
			}
		}

		// 3 - look in default of docfield
		if (df['default']) {

			if (df["default"] == "__user" || df["default"].toLowerCase() == "user") {
				return frappe.session.user;

			} else if (df["default"] == "user_fullname") {
				return frappe.session.user_fullname;

			} else if (df["default"] == "Today") {
				return frappe.datetime.get_today();

			} else if ((df["default"] || "").toLowerCase() === "now") {
				return frappe.datetime.now_datetime();

			} else if (df["default"][0]===":") {
				var boot_doc = frappe.model.get_default_from_boot_docs(df, doc, parent_doc);
				var is_allowed_boot_doc = !has_user_permissions || allowed_records.includes(boot_doc);

				if (is_allowed_boot_doc) {
					return boot_doc;
				}
			} else if (df.fieldname===meta.title_field) {
				// ignore defaults for title field
				return "";
			}

			// is this default value is also allowed as per user permissions?
			var is_allowed_default = !has_user_permissions || allowed_records.includes(df.default);
			if (df.fieldtype!=="Link" || df.options==="User" || is_allowed_default) {
				return df["default"];
			}

		} else if (df.fieldtype=="Time") {
			return frappe.datetime.now_time();
		}
	},

	get_default_from_boot_docs: function(df, doc, parent_doc) {
		// set default from partial docs passed during boot like ":User"
		if(frappe.get_list(df["default"]).length > 0) {
			var ref_fieldname = df["default"].slice(1).toLowerCase().replace(" ", "_");
			var ref_value = parent_doc ?
				parent_doc[ref_fieldname] :
				frappe.defaults.get_user_default(ref_fieldname);
			var ref_doc = ref_value ? frappe.get_doc(df["default"], ref_value) : null;

			if(ref_doc && ref_doc[df.fieldname]) {
				return ref_doc[df.fieldname];
			}
		}
	},

	add_child: function(parent_doc, doctype, parentfield, idx) {
		// if given doc, fieldname only
		if(arguments.length===2) {
			parentfield = doctype;
			doctype = frappe.meta.get_field(parent_doc.doctype, parentfield).options;
		}

		// create row doc
		idx = idx ? idx - 0.1 : (parent_doc[parentfield] || []).length + 1;

		var child = frappe.model.get_new_doc(doctype, parent_doc, parentfield);
		child.idx = idx;

		// renum for fraction
		if(idx !== cint(idx)) {
			var sorted = parent_doc[parentfield].sort(function(a, b) { return a.idx - b.idx; });
			for(var i=0, j=sorted.length; i<j; i++) {
				var d = sorted[i];
				d.idx = i + 1;
			}
		}

		if (cur_frm && cur_frm.doc == parent_doc) cur_frm.dirty();

		return child;
	},

	copy_doc: function(doc, from_amend, parent_doc, parentfield) {
		var no_copy_list = ['name','amended_from','amendment_date','cancel_reason'];
		var newdoc = frappe.model.get_new_doc(doc.doctype, parent_doc, parentfield);

		for(var key in doc) {
			// dont copy name and blank fields
			var df = frappe.meta.get_docfield(doc.doctype, key);

			if (df && key.substr(0, 2) != '__'
				&& !in_list(no_copy_list, key)
				&& !(df && (!from_amend && cint(df.no_copy) == 1))) {

				var value = doc[key] || [];
				if (frappe.model.table_fields.includes(df.fieldtype)) {
					for (var i = 0, j = value.length; i < j; i++) {
						var d = value[i];
						frappe.model.copy_doc(d, from_amend, newdoc, df.fieldname);
					}
				} else {
					newdoc[key] = doc[key];
				}
			}
		}

		if (typeof doc.dont_copy_current_rate !== 'undefined' && doc.dont_copy_current_rate == 0){
			var newdoc_items = newdoc.items || [];
			console.log("olddoc items", doc.items)
			console.log("newdoc items", newdoc_items)
			setTimeout(function(){ 
				for (var i = 0; i < newdoc_items.length; i++) {
					frappe.model.set_value(newdoc.items[i].doctype, newdoc.items[i].name, 'rate', doc.items[i].rate);
				}
				
			}, 2000);
		}

		var user = frappe.session.user;

		newdoc.__islocal = 1;
		newdoc.docstatus = 0;
		newdoc.owner = user;
		newdoc.creation = '';
		newdoc.modified_by = user;
		newdoc.modified = '';

		return newdoc;
	},

	open_mapped_doc: function(opts) {
		console.log("open_mapped_doc", opts)
		if (opts.frm && opts.frm.doc.__unsaved) {
			frappe.throw(__("You have unsaved changes in this form. Please save before you continue."));

		} else if (!opts.source_name && opts.frm) {
			opts.source_name = opts.frm.doc.name;

		// Allow opening a mapped doc without a source document name
		} else if (!opts.frm) {
			opts.source_name = null;
		}

		return frappe.call({
			type: "POST",
			method: 'frappe.model.mapper.make_mapped_doc',
			args: {
				method: opts.method,
				source_name: opts.source_name,
				args: opts.args || null,
				selected_children: opts.frm ? opts.frm.get_selected() : null
			},
			freeze: true,
			callback: function(r) {
				if(!r.exc) {
					frappe.model.sync(r.message);
					if(opts.run_link_triggers) {
						frappe.get_doc(r.message.doctype, r.message.name).__run_link_triggers = true;
					}
					frappe.set_route("Form", r.message.doctype, r.message.name);
				}
			}
		})
	}
});

frappe.create_routes = {};
frappe.new_doc = function (doctype, opts, init_callback) {
	if (doctype === 'File') {
		new frappe.ui.FileUploader({
			folder: opts ? opts.folder : 'Home'
		});
		return;
	}
	return new Promise(resolve => {
		if(opts && $.isPlainObject(opts)) {
			frappe.route_options = opts;
		}
		frappe.model.with_doctype(doctype, function() {
			if(frappe.create_routes[doctype]) {
				frappe.set_route(frappe.create_routes[doctype])
					.then(() => resolve());
			} else {
				frappe.ui.form.make_quick_entry(doctype, null, init_callback)
					.then(() => resolve());
			}
		});

	});
}

function check_foreign_customers(customer) {
    if (customer) {
        frappe.call({
            'method': "energielenker.energielenker.sales_invoice.sales_invoice.get_vat_template",
            'args': {
                'customer': customer
            },
            'callback': function(response) {
                if (response.message) {
                    let taxes = response.message
                    cur_frm.set_value('taxes_and_charges', taxes);
                } else {
                    cur_frm.set_value('taxes_and_charges', null);
                }
            }
        });
    } else {
        cur_frm.set_value('taxes_and_charges', null);
    }
}

function fetch_stock_items(item_code, cdt, cdn) {
    frappe.call({
        method: "frappe.client.get_value",
        args: {
            doctype: "Item",
            filters: {
                name: item_code
            },
            fieldname: "is_stock_item" 
        },
        callback: function(response) {
            if (response.message.is_stock_item) {
                frappe.model.set_value(cdt, cdn, "maintain_stock", 1);
            }
        }
    });
}

function check_deactivation(item_code) {
    frappe.call({
        'method': "frappe.client.get",
        'args': {
            'doctype': "Item",
            'name': item_code
        },
        'callback': function(response) {
            if (response.message && response.message.temporarily_deactivated) {
                frappe.msgprint("Artikel " + item_code + " ist vorübergehend deaktiviert");
            }
        }
    });
}

function check_deactivated_items(frm) {
    frappe.call({
        'method': 'energielenker.energielenker.utils.utils.get_deactivated_items',
        'args': {
            'doc': frm.doc
        },
        'callback': function(response) {
            if (response.message) {
                let deactivated_items = response.message;
                let message = `Folgende Artikel sind vorübergehend deaktiviert:<br>`
                for (let i = 0; i < deactivated_items.length; i++) {
                    message = message + `<br>${deactivated_items[i]}`
                }
                frappe.msgprint(message);
                frappe.validated=false;
            }
        }
    });
}

function set_project_manager(project) {
    if (project) {
        frappe.call({
            'method': 'frappe.client.get',
            'args': {
                'doctype': "Project",
                'doc': project
            },
            'callback': function(response) {
                if (response.message) {
                    cur_frm.set_value("project_manager_name", response.message.project_manager_name);
                }
            }
        });
    } else {
        cur_frm.set_value("project_manager_name", null);
    }
}
