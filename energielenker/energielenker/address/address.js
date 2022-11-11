frappe.ui.form.on('Address', {
    validate: function(frm) {
        if (cur_frm.doc.plz) {
            cur_frm.set_value('pincode', cur_frm.doc.plz);
        } else {
            cur_frm.set_value('pincode', '');
        }
        if (cur_frm.doc.company_adr_line2) {
           cur_frm.set_value('address_line2', cur_frm.doc.company_adr_line2);
        } else {
           cur_frm.set_value('address_line2', '');
        }
    },
    refresh: function(frm) {
        set_timestamps(frm);
        cur_frm.fields_dict['support_wird_verrechnet_ueber'].get_query = function(doc) {
             return {
                 filters: {
                     "ist_support_kunde": 1
                 }
             }
        }
    }
})

// Change the timeline specification, from "X days ago" to the exact date and time
function set_timestamps(frm){
    setTimeout(function() {
        // mark navbar
        var timestamps = document.getElementsByClassName("frappe-timestamp");
        for (var i = 0; i < timestamps.length; i++) {
            timestamps[i].innerHTML = timestamps[i].title
        }
    }, 1000);
}
