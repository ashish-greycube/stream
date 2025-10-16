// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Event Sync Log GC', {
	refresh: function (frm) {
		if (frm.doc.status == "Failed") {
			frm.add_custom_button(__("Resync"), function () {
				frappe.call({
					method: "stream.stream.doctype.event_producer_gc.event_producer_gc.resync",
					args: {
						update: frm.doc,
					},
					callback: function (r) {
						if (r.message) {
							frappe.msgprint(r.message);
							frm.set_value("status", r.message);
							frm.save();
						}
					},
				});
			});
		}
	},
});
