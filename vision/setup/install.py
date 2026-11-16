import frappe

def after_install():
    print("Running Vision after_install setup...")
    setup_domains()
    create_default_leave_types()
    from vision.vision.update_field_options import update_employee_checkin_custom_fields
    update_employee_checkin_custom_fields()
    print("Vision setup complete.")

def setup_domains():
    print("Configuring standard Domains...")
    try:
        if frappe.db.exists("Domain Settings", "Domain Settings"):
            domain_settings = frappe.get_doc("Domain Settings")
            if not domain_settings.active_domains:
                domain_settings.append("active_domains", {"domain": "HR"})
            domain_settings.save(ignore_permissions=True)
    except Exception as e:
        print(f"Failed to setup domains: {e}")

def create_default_leave_types():
    print("Creating default Leave Types...")
    default_leaves = [
        {"leave_type_name": "Sick Leave", "is_lwp": 0, "is_earned_leave": 0},
        {"leave_type_name": "Casual Leave", "is_lwp": 0, "is_earned_leave": 0},
        {"leave_type_name": "Leave Without Pay", "is_lwp": 1, "is_earned_leave": 0},
    ]

    for leave in default_leaves:
        if not frappe.db.exists("Leave Type", leave["leave_type_name"]):
            try:
                doc = frappe.get_doc({
                    "doctype": "Leave Type",
                    **leave
                })
                doc.insert(ignore_permissions=True)
            except Exception as e:
                print(f"Could not create Leave Type {leave['leave_type_name']}: {e}")
