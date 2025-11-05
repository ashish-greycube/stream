# Copyright (c) 2025, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	columns = get_columns()
	report_data = get_data(filters)
	
	if not report_data:
		frappe.msgprint(_("No records found"))
		return columns,report_data
	
	return columns, report_data

def get_columns():
	return [
		{
			"fieldname": "doctype",
			"label": _("Document Type"),
			"fieldtype": "Data",
			"width": 120
		},
		{
			"fieldname": "docname",
			"label": _("Document Name"),
			"fieldtype": "Dynamic Link",
			"options": "doctype",
			"width": 180,
		},
		{
			"fieldname": "posting_date",
			"label":_("Posting Date"),
			"fieldtype": "Date",
			"width":200
		},
		{
			"fieldname": "payment_type",
			"label":_("Payment Type"),
			"fieldtype": "Select",
			"options": "\nBank\nCash",
			"width":200
		},
		{
			"fieldname": "party_type",
			"label":_("Party Type"),
			"fieldtype": "Data",
			"width":200
		},
		{
			"fieldname": "party",
			"label":_("Party"),
			"fieldtype": "Dynamic Link",
			"options": "party_type",
			"width":300
		},
		{
			"fieldname": "amount",
			"label":_("Amount"),
			"fieldtype": "Currency",
			"width":200
		},
		{
			"fieldname": "found_in_gov",
			"label":_("Found in GOV"),
			"fieldtype": "Select",
			"options": "\nYes\nNo",
			"width":200
		}
	]

def get_data(filters):
	conditions, conditions_2 = get_conditions(filters)
	sync_data = []
	if filters.get("party_type") == "Customer":
		sales_invoice_data = frappe.db.sql("""
			select
				'Sales Invoice' as doctype,
				name as docname,
				posting_date,
				custom_payment_type as payment_type,
				customer as party,
				'Customer' as party_type,
				grand_total as amount,
				case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
			from
				`tabSales Invoice` si
			where
				docstatus = 1
				{0}
			order by
				creation desc
		""".format(conditions), filters, as_dict=1,debug=1)
		sync_data.extend(sales_invoice_data)

		delivery_note_data = frappe.db.sql("""
			select
				'Delivery Note' as doctype,
				name as docname,
				posting_date,
				custom_payment_type as payment_type,
				customer as party,
				'Customer' as party_type,
				grand_total as amount,
				case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
			from
				`tabDelivery Note` dn
			where
				docstatus = 1
				{0}
			order by
				creation desc
		""".format(conditions), filters, as_dict=1)
		sync_data.extend(delivery_note_data)

	conditions_for_payment_entry = ""
	if filters.get("party_type"):
		conditions_for_payment_entry += " and party_type = '{0}'".format(filters.get("party_type"))
	if len(filters.get("party"))>0:
		conditions_for_payment_entry += " and party in ('{0}')".format("','".join(filters.get("party")))
	payment_entry_data = frappe.db.sql("""
		select
			'Payment Entry' as doctype,
			name as docname,
			posting_date,
			custom_payment_type as payment_type,
			party as party,
			party_type as party_type,
			paid_amount as amount,
			case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
		from
			`tabPayment Entry` pe
		where
			docstatus = 1 {0}
			{1}
		order by
			creation desc
	""".format(conditions_for_payment_entry,conditions_2), filters, as_dict=1)
	
	sync_data.extend(payment_entry_data)

	if filters.get("party_type") == "Supplier":

		conditions_for_supplier = ""
		if len(filters.get("party"))>0:
			conditions_for_supplier += " and supplier in ('{0}')".format("','".join(filters.get("party")))

		purchase_invoice_data = frappe.db.sql("""
			select
				'Purchase Invoice' as doctype,
				name as docname,
				posting_date,
				custom_payment_type as payment_type,
				supplier as party,
				'Supplier' as party_type,
				grand_total as amount,
				case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
			from
				`tabPurchase Invoice` pi
			where
				docstatus = 1
				{0} {1}
			order by
				creation desc
		""".format(conditions_for_supplier, conditions_2), filters, as_dict=1)
		sync_data.extend(purchase_invoice_data)

		purchase_receipt_data = frappe.db.sql("""
			select
				'Purchase Receipt' as doctype,
				name as docname,
				posting_date,
				custom_payment_type as payment_type,
				supplier as party,
				'Supplier' as party_type,
				grand_total as amount,
				case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
			from
				`tabPurchase Receipt` pr
			where
				docstatus = 1
				{0} {1}
			order by
				creation desc
		""".format(conditions_for_supplier, conditions_2), filters, as_dict=1)
		sync_data.extend(purchase_receipt_data)

	journal_entry_data = frappe.db.sql("""
		select
			'Journal Entry' as doctype,
			name as docname,
			posting_date,
			custom_payment_type as payment_type,
			total_debit as amount,
			case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
		from
			`tabJournal Entry` je
		where
			docstatus = 1
			{0}
		order by
			creation desc
	""".format(conditions_2), filters, as_dict=1)
	sync_data.extend(journal_entry_data)

	stock_entry_data = frappe.db.sql("""
		select
			'Stock Entry' as doctype,
			name as docname,
			posting_date,
			custom_payment_type as payment_type,
			total_amount as amount,	
			case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
		from
			`tabStock Entry` se
		where
			docstatus = 1
			{0}
		order by
			creation desc
	""".format(conditions_2), filters, as_dict=1)
	sync_data.extend(stock_entry_data)

	stock_reconciliation_data = frappe.db.sql("""
		select
			'Stock Reconciliation' as doctype,
			name as docname,
			posting_date,
			custom_payment_type as payment_type,
			difference_amount as amount,	
			case when (custom_gov_modified > modified) then 'Yes' else 'No' end as found_in_gov
		from
			`tabStock Reconciliation` sr
		where
			docstatus = 1
			{0}
		order by
			creation desc
	""".format(conditions_2), filters, as_dict=1)
	sync_data.extend(stock_reconciliation_data)

	return sync_data

def get_conditions(filters):
	conditions = ""
	if len(filters.get("party"))>0:
		conditions += " and customer in ('{0}')".format("','".join(filters.get("party")))
	if filters.get("payment_type"):
		conditions += " and custom_payment_type = '{0}'".format(filters.get("payment_type"))

	conditions_2 = ""
	if filters.get("payment_type"):
		conditions_2 += " and custom_payment_type = '{0}'".format(filters.get("payment_type"))

	return conditions, conditions_2