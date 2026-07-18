import frappe

def license_guard(doc, method):
    # Skip for Frappe core doctypes (allow login, user management, etc. to continue)
    if doc.doctype in ['User', 'Error Log', 'Error Snapshot', 'Scheduled Job Log', 'Activity Log', 'Session Default Settings', 'System Settings', 'Role', 'Has Role', 'DocType']:
        return

    # Skip if it is a background task doing something internal
    if frappe.flags.in_patch or frappe.flags.in_migrate or frappe.flags.in_import:
        return

    license_status = frappe.db.get_single_value('Vaaman Settings', 'license_status') or 'Active'
    
    if license_status != 'Active':
        frappe.throw(
            "Access Denied: Your Elevate HR License is expired or inactive. Please contact Octavision HQ for renewal.",
            title="License Expired"
        )

def verify_license_with_hq():
    # This runs nightly via scheduler
    hq_url = frappe.conf.get('hq_url') or "https://cnd.octavision.in"
    api_key = frappe.conf.get('hq_api_key')
    api_secret = frappe.conf.get('hq_api_secret')
    client_site = frappe.local.site
    
    if not api_key or not api_secret:
        return # Cannot verify, fail open or closed? Let's leave it as is if not configured yet.
        
    import requests
    try:
        response = requests.post(
            f"{hq_url}/api/method/octavision_hq.api.verify_license",
            headers={
                "Authorization": f"token {api_key}:{api_secret}",
                "Content-Type": "application/json"
            },
            json={"license_key": api_key},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json().get('message', {})
            status = data.get('status', 'Active')
            
            # Update local license status
            if frappe.db.exists('Vaaman Settings', 'Vaaman Settings'):
                frappe.db.set_value('Vaaman Settings', 'Vaaman Settings', 'license_status', status)
                frappe.db.commit()
    except Exception as e:
        frappe.log_error(title="HQ License Verification Failed", message=str(e))
