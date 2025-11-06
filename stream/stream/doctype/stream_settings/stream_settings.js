// Copyright (c) 2025, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stream Settings', {
	sync: function(frm) {
		if (!frm.doc.from_date || !frm.doc.to_date){
			frappe.throw(__("Please set From Date and To Date first"))
		}
		frappe.call({
			method: "stream.api.sync_doctypes",
			args: {
				from_date: frm.doc.from_date,
				to_date: frm.doc.to_date
			},
			callback: function(r) {
				console.log(r.message);
			}
				
				})
	}
});
