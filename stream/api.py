import frappe
from frappe import _
import requests
# from stream.stream.doctype.event_update_log_gc.event_update_log_gc import sync_from_button
from stream.stream.doctype.event_update_log_gc.event_update_log_gc import check_doctype_has_consumers, get_update, make_event_update_log

@frappe.whitelist()
def sync_from_button(doc):
	"""called via button"""
	if isinstance(doc, str):
		doc = frappe.parse_json(doc)

	print("==============",type(doc),doc.doctype,doc.name)
	if frappe.flags.in_install or frappe.flags.in_migrate:
		return
	
	if check_doctype_has_consumers(doc.doctype):

		event_consumer_details = frappe.get_all(
			"Event Consumer Document Type GC",
			filters={"ref_doctype": doc.doctype, "status": "Approved", "unsubscribed": 0},
			ignore_ddl=True,
			fields=["name","parent"]
		)
		if len(event_consumer_details)>0:
			for detail in event_consumer_details:
				site_url = detail.parent
				print(site_url,"------------------------------------------")

				api_key = frappe.db.get_value("Event Consumer GC",
											  {"name":detail.parent},
											  "api_key")
				
				generated_secret = frappe.utils.password.get_decrypted_password(
				"Event Consumer GC", detail.parent, fieldname="api_secret"
				)
				
				headers = {
					"Accept": "application/json",
					"Content-Type": "application/json",
					"Authorization": "token {0}:{1}".format(api_key,generated_secret)
					}
				
				response = requests.get("{0}/api/resource/{1}/{2}".format(site_url,doc.doctype,doc.name), headers=headers)
				print(response.status_code)
				print(response.json())

				if response.status_code == 200:
					old_data = response.json().get("data")
					doc = frappe.get_doc(doc.doctype, doc.name)	
					# print(doc.meta.fields)
					new_data = doc
					
					if not doc.flags.event_update_log:
						diff = get_update(old_data, new_data)
						if diff:
							doc.diff = diff
							make_event_update_log(doc, update_type="Update")
				
				if response.status_code == 404:
					doc = frappe.get_doc(doc.doctype, doc.name)
					doc.flags.event_update_log = make_event_update_log(doc, update_type="Create")

				copy_creation_of_consumer_site(doc, None)
				frappe.msgprint("Event Update Log is Created. Please check Event Sync Log on Consumer site.",alert=True)

def copy_creation_of_consumer_site(doc, method):
    # print("*"*100)
    is_producer_site = check_if_producer_site()
    if is_producer_site == True:
        # if check_doctype_has_consumers(doc.doctype):
            event_consumer_details = frappe.get_all(
			"Event Consumer Document Type GC",
			filters={"ref_doctype": doc.doctype, "status": "Approved", "unsubscribed": 0},
			ignore_ddl=True,
			fields=["name","parent"]
		)
            
            if len(event_consumer_details)>0:
                for detail in event_consumer_details:
                    site_url = detail.parent

                    api_key = frappe.db.get_value("Event Consumer GC",
                                                {"name":detail.parent},
                                                "api_key")
                    
                    generated_secret = frappe.utils.password.get_decrypted_password(
                    "Event Consumer GC", detail.parent, fieldname="api_secret"
                    )
                    
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": "token {0}:{1}".format(api_key,generated_secret)
                        }
                    response = requests.get('{0}/api/resource/{1}?fields=["name","creation","modified"]&filters=[["name","=","{2}"]]'.format(site_url,doc.doctype,doc.name), headers=headers)
                    print(response.status_code)
                    print(response.json())
                    if len(response.json().get("data"))>0:
                        data = response.json().get("data")[0]
                        print(data,"=========================")

                        frappe.db.set_value(doc.doctype, doc.name, "custom_gov_creation",data.get("creation"),update_modified=False)
                        frappe.db.set_value(doc.doctype, doc.name, "custom_gov_modified",data.get("modified"),update_modified=False)


def check_if_producer_site():
    event_consumer_record_exists = frappe.db.exists("Event Consumer GC", {"docstatus":0})
    if event_consumer_record_exists:
        return True
    else:
        return False
    
@frappe.whitelist()
def sync_doctypes(from_date, to_date):
    doctypes_to_sync = get_doctype_to_sync()
    print(doctypes_to_sync,"---------------")
    from stream.stream.report.sync_report.sync_report import execute
    unsync_data_from_sync_report = execute(filters={"from_date":from_date,"to_date":to_date,"found_in_gov":"No"})[1]
    print(unsync_data_from_sync_report,"==============")

    if len(doctypes_to_sync)>0:
        for doctype in doctypes_to_sync:
            if len(unsync_data_from_sync_report)>0:
                for row in unsync_data_from_sync_report:
                    # print(doctype, row,"+++++")
                    if doctype == row.doctype:
                        doc = frappe.get_doc(doctype,row.docname)
                        sync_from_button(doc)


def get_doctype_to_sync():
    is_producer_site = check_if_producer_site()
    if is_producer_site == True:
        doctypes = frappe.get_all(
            "Event Consumer Document Type GC",
            filters={"status": "Approved", "unsubscribed": 0},
            ignore_ddl=True,
            fields=["ref_doctype"]
        )
        doctype_list = []
        for d in doctypes:
            doctype_list.append(d.ref_doctype)
        return doctype_list
    else:
        return []