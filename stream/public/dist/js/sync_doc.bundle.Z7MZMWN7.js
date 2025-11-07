(() => {
  // ../stream/stream/public/js/sync_doc.bundle.js
  $(document).on("form-refresh", function(event, frm) {
    console.log("=====Sync======");
    if (frappe.meta.has_field(frm.doc.doctype, "custom_payment_type") && frm.is_new() == void 0) {
      console.log("--------has field-----------");
      frappe.db.get_list("Event Producer GC", {
        fields: ["name"],
        filters: {
          docstatus: 0
        }
      }).then((records) => {
        console.log(records, records.length);
        if (records.length > 0) {
          return;
        } else {
          console.log("Inside IFFF");
          frm.add_custom_button(__("Sync"), function() {
            console.log("Sync");
            frappe.call({
              method: "stream.api.sync_from_button",
              args: {
                doc: frm.doc
              },
              callback: function(r) {
                console.log(r);
              }
            });
          });
        }
      });
    }
  });
})();
//# sourceMappingURL=sync_doc.bundle.Z7MZMWN7.js.map
