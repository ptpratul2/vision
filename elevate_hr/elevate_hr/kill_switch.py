import frappe

def check_license_before_request():
    if not getattr(frappe, "request", None):
        return
        
    # Allow Guest and Administrator to bypass the block
    if frappe.session.user in ["Guest", "Administrator"]:
        return
        
    # Allow logout requests so users can sign out if they are trapped
    if frappe.request.path.startswith("/api/method/logout"):
        return
        
    # Allow HQ API endpoints so the HQ server can still verify licenses
    if frappe.request.path.startswith("/api/method/octavision_hq."):
        return

    license_status = frappe.db.get_single_value('Vaaman Settings', 'license_status') or 'Expired'
    
    if license_status != 'Active':
        frappe.throw(
            "Access Denied: Your Elevate HR License is expired or inactive. Please contact Octavision HQ for renewal.",
            title="License Expired"
        )
def license_guard(doc, method):
    # Skip for Frappe core doctypes (allow login, user management, etc. to continue)
    if doc.doctype in ['User', 'Error Log', 'Error Snapshot', 'Scheduled Job Log', 'Activity Log', 'Session Default Settings', 'System Settings', 'Role', 'Has Role', 'DocType', 'Vaaman Settings', 'DefaultValue']:
        return

    # Skip if it is a background task doing something internal
    if frappe.flags.in_patch or frappe.flags.in_migrate or frappe.flags.in_import:
        return

    license_status = frappe.db.get_single_value('Vaaman Settings', 'license_status') or 'Expired'
    
    if license_status != 'Active':
        frappe.throw(
            "Access Denied: Your Elevate HR License is expired or inactive. Please contact Octavision HQ for renewal.",
            title="License Expired"
        )

def verify_license_with_hq():
    # This runs nightly via scheduler
    from frappe.utils import now_datetime, get_datetime, add_days
    import requests

    hq_url = (frappe.conf.get('hq_url') or "https://cnd.octavision.in").rstrip('/')
    license_key = frappe.conf.get('elevate_hr_licence_key')
    
    frappe.log_error(title="License Sync: Start", message=f"Checking license with HQ. Key: {license_key}, URL: {hq_url}")
    
    # 1. Missing Key -> Immediate Lock
    if not license_key:
        frappe.log_error(title="License Sync: Missing Key", message="No elevate_hr_licence_key found in site_config.json. Marking as Expired.")
        if frappe.db.exists('Vaaman Settings', 'Vaaman Settings'):
            frappe.db.set_value('Vaaman Settings', 'Vaaman Settings', 'license_status', 'Expired')
            frappe.db.commit()
        return 
        
    try:
        url = f"{hq_url}/api/method/octavision_hq.api.verify_license"
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            params={"license_key": license_key},
            json={"license_key": license_key},
            timeout=10
        )
        
        # 2. Explicit Verification Result from HQ
        if response.status_code == 200:
            data = response.json().get('message', {})
            status = data.get('status', 'Expired')
            
            frappe.log_error(title="License Sync: Success", message=f"Parsed status from HQ: {status}. Updating local DB.")
            
            if status == 'Active':
                # Update last successful sync timestamp
                frappe.db.set_default('elevate_hr_last_sync', str(now_datetime()))
                
            # Update local license status
            if frappe.db.exists('Vaaman Settings', 'Vaaman Settings'):
                frappe.db.set_value('Vaaman Settings', 'Vaaman Settings', 'license_status', status)
                frappe.db.commit()
            return

        # 3. Explicit Denial / Malformed Config (401, 403, 404) -> Immediate Lock
        if response.status_code in [401, 403, 404]:
            frappe.log_error(title="License Sync: Auth/Not Found", message=f"Received {response.status_code}. Marking as Expired.")
            if frappe.db.exists('Vaaman Settings', 'Vaaman Settings'):
                frappe.db.set_value('Vaaman Settings', 'Vaaman Settings', 'license_status', 'Expired')
                frappe.db.commit()
            return

        # 4. Unexpected HQ Server Error (e.g. 500, 502) -> Trigger Grace Period logic
        raise Exception(f"Unexpected HTTP Status: {response.status_code}")

    except Exception as e:
        # Grace Period Logic for Network / Timeout / Server Errors
        last_sync_str = frappe.db.get_default('elevate_hr_last_sync')
        if last_sync_str:
            last_sync = get_datetime(last_sync_str)
            if now_datetime() <= add_days(last_sync, 3):
                # Within 3-day grace period
                frappe.log_error(title="License Sync: Grace Period Active", message=f"Network/HQ error, but within 3-day grace period. Error: {str(e)}")
                return

        # Outside grace period (or never successfully synced) -> Lock
        frappe.log_error(title="License Sync: Grace Period Expired", message=f"Network error and grace period expired. Marking as Expired. Error: {str(e)}")
        if frappe.db.exists('Vaaman Settings', 'Vaaman Settings'):
            frappe.db.set_value('Vaaman Settings', 'Vaaman Settings', 'license_status', 'Expired')
            frappe.db.commit()

