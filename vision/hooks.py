# in hooks.py
from .vision.patches import apply_monkey_patch
app_name = "vision"
app_title = "Vision"
app_publisher = "Pratul Tripathi"
app_description = "Exended Feature for HR Module"
app_email = "ptpratul2@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vision/css/vision.css"
# app_include_js = "/assets/vision/js/vision.js"

# include js, css files in header of web template
# web_include_css = "/assets/vision/css/vision.css"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vision/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/salary_structure_assignment.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vision/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "vision.utils.jinja_methods",
# 	"filters": "vision.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vision.install.before_install"
after_install = "vision.setup.install.after_install"
before_app_install = "vision.vision.patches.apply_monkey_patch"

after_migrate = [
    "vision.vision.update_field_options.update_earned_leave_frequency_options",
    "vision.vision.update_field_options.update_attendance_status_options",
    "vision.vision.update_field_options.update_attendance_request_reason_options",
    "vision.vision.update_field_options.update_attendance_request_custom_fields",
    "vision.vision.update_field_options.update_employee_checkin_custom_fields",
]



# Uninstallation
# ------------

# before_uninstall = "vision.uninstall.before_uninstall"
# after_uninstall = "vision.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vision.utils.before_app_install"
# after_app_install = "vision.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vision.utils.before_app_uninstall"
# after_app_uninstall = "vision.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vision.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

override_doctype_class = {
        "Attendance": "vision.vision.api.vision" ,
        "Attendance Request": "vision.overrides.attendance_request.CustomAttendanceRequest",
        "Compensatory Leave Request": "vision.vision.compoff.CompOff",
        "Leave Policy Assignment": "vision.overrides.leave_policy_assignment.CustomLeavePolicyAssignment",
        "Salary Slip": "vision.overrides.salary_slip.CustomSalarySlip"
        } 


     
# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
    "*": {
        "before_insert": "vision.vision.kill_switch.license_guard",
        "before_save": "vision.vision.kill_switch.license_guard",
    },
    "Attendance": {
        "after_insert": "vision.vision.half_day_leaves.validate_half_day_attendance"
    },
    
    "OverTime Import": {
        "validate": "vision.vision.over_time.validate_overtime_import_comp_off",
        "on_submit": "vision.vision.over_time.calculate_compensatory_leave",
        "on_cancel": "vision.vision.over_time.cancel_compensatory_leave",
        "on_update_after_submit": "vision.vision.over_time.recalculate_compensatory_leave_on_update",
    },
    "Payment Request": {
        "on_submit": "vision.purchase_invoice.validate_invoice_outstanding"
    },
        "Salary Slip": {
        "before_save": "vision.vision.salary_slip_hooks.calculate_overtime_hours",
        "validate":[ "vision.vision.weekly_off.set_total_weekly_off",
                    "vision.vision.weekly_off.before_save"]
    },
    "App Push Notification": {
        "on_submit": "vision.api2.send_fcm_notification"
    },
    "App Announcement": {
        "on_submit": "vision.api2.send_fcm_notification"
    },
    "Purchase Receipt": {
        "on_submit": "vision.draft_purchase_invoice.auto_create_purchase_invoice"
    },
    "Salary Structure Assignment": {
        "before_save": "vision.vision.salery_component_field_add_buttton.on_salary_assignment_update"
    }

}


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vision.tasks.all"
# 	],
	# "daily": [
	# 	"vision.vision.salery_component_field_add_buttton.update_history",
	# ],
# 	"hourly": [
# 		"vision.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vision.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vision.tasks.monthly"
# 	],
# }
# scheduler_events = {
    # "daily": [
    #     "vision.purchase_invoice.create_payment_request"
    # ],
    # "all": [
    #     "vision.purchase_invoice.create_payment_request"
    # ],
    # "cron": {
    #     "* * * * *": [  # Runs every minute
    #         "vision.purchase_invoice.create_payment_request"
    #     ]
    # }
# }

scheduler_events = {
    "daily": [
        "vision.late_entry_atten.process_attendance_policy",
        "vision.vision.salery_component_field_add_buttton.update_history"
    ],
    "cron": {
        # "*/5 * * * *": [
        #     "vision.api2.check_and_send_shift_reminders",
        #     "vision.vision.kill_switch.verify_license_with_hq"
        # ],
        "0 23 * * *": [
            "vision.holiday_policy.process_holiday_sandwich_policy"
        ]
    }
}


# Testing
# -------

# before_tests = "vision.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vision.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vision.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
before_request = ["vision.vision.kill_switch.check_license_before_request"]
# after_request = ["vision.utils.after_request"]

# Job Events
# ----------
# before_job = ["vision.utils.before_job"]
# after_job = ["vision.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"vision.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

#custom_field_add
fixtures = [
    {"dt":"Custom Field","filters":[["module","=","Vision"]]},
    {"dt":"Property Setter","filters":[["module","=","Vision"]]},
    {"dt":"Client Script","filters":[["module","=","Vision"]]},
    {"dt":"Server Script","filters":[["module","=","Vision"]]},
    {"dt":"Workflow","filters":[["module","=","Vision"]]},
    {"dt":"Workflow State","filters":[["module","=","Vision"]]},
    {"dt":"Workflow Action Master","filters":[["module","=","Vision"]]},
    {"dt":"Print Format","filters":[["module","=","Vision"]]}
]
# Ensure the function is called during startup
apply_monkey_patch()
