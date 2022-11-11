frappe.ui.form.on('Material Request', {
    refresh: function(frm) {
        set_timestamps(frm);
        setTimeout(function(){ 
          cur_frm.fields_dict.items.grid.get_field('item_code').get_query =   
             function() {                                                                      
                return {
                   query: "energielenker.energielenker.item.item.item_query",
                   filters: {}
                }
             }
        }, 1000);
    },
    validate: function(frm) {
        if (cur_frm.doc.project) {
            copy_project(frm);
        }
    }
})

function copy_project(frm) {
    var items = cur_frm.doc.items;
    items.forEach(function(entry) {
        entry.project = cur_frm.doc.project
    });
    cur_frm.refresh_field('items');
}

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
