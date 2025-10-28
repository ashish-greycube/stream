$(document).on("form-refresh", function (event, frm) {
    console.log("=====Sync======")
    if (frappe.meta.has_field(frm.doc.doctype, "custom_payment_type") ) {
        console.log("--------has field-----------")
        if (
            frm.is_new() == undefined
        ) {
            console.log("Inside IFFF")
            frm.add_custom_button(__("Sync"), function() {
                console.log("Sync")
                frappe.call({
                    method: "stream.stream.doctype.event_update_log_gc.event_update_log_gc.notify_consumers",
                    args: {
                        doc: frm.doc,
                        event:'sycn',
                        sync_type:'sync'
                    },
                    callback: function (r) {
                        console.log(r)
                    }	
                })	
            })
        }
    }
});