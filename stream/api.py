import frappe
from frappe import _
import requests
from stream.stream.doctype.event_update_log_gc.event_update_log_gc import check_doctype_has_consumers

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

                        frappe.db.set_value(doc.doctype, doc.name, "custom_gov_creation",data.get("creation"))
                        frappe.db.set_value(doc.doctype, doc.name, "custom_gov_modified",data.get("modified"))


def check_if_producer_site():
    event_consumer_record_exists = frappe.db.exists("Event Consumer GC", {"docstatus":0})
    if event_consumer_record_exists:
        return True
    else:
        return False