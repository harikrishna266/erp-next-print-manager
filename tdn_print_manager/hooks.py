app_name = "tdn_print_manager"
app_title = "TDN Print Manager"
app_publisher = "Blurd Technologies Private Limited"
app_description = "Print shop MES - specs, pricing, job sheets, sessions"
app_email = "contact@3dn.app"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tdn_print_manager",
# 		"logo": "/assets/tdn_print_manager/logo.png",
# 		"title": "TDN Print Manager",
# 		"route": "/tdn_print_manager",
# 		"has_permission": "tdn_print_manager.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tdn_print_manager/css/tdn_print_manager.css"
# app_include_js = "/assets/tdn_print_manager/js/tdn_print_manager.js"

# include js, css files in header of web template
# web_include_css = "/assets/tdn_print_manager/css/tdn_print_manager.css"
# web_include_js = "/assets/tdn_print_manager/js/tdn_print_manager.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tdn_print_manager/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tdn_print_manager/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tdn_print_manager.utils.jinja_methods",
# 	"filters": "tdn_print_manager.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tdn_print_manager.install.before_install"
# after_install = "tdn_print_manager.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tdn_print_manager.uninstall.before_uninstall"
# after_uninstall = "tdn_print_manager.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tdn_print_manager.utils.before_app_install"
# after_app_install = "tdn_print_manager.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tdn_print_manager.utils.before_app_uninstall"
# after_app_uninstall = "tdn_print_manager.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "tdn_print_manager.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tdn_print_manager.notifications.get_notification_config"

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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tdn_print_manager.tasks.all"
# 	],
# 	"daily": [
# 		"tdn_print_manager.tasks.daily"
# 	],
# 	"hourly": [
# 		"tdn_print_manager.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tdn_print_manager.tasks.weekly"
# 	],
# 	"monthly": [
# 		"tdn_print_manager.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "tdn_print_manager.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "tdn_print_manager.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tdn_print_manager.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tdn_print_manager.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tdn_print_manager.utils.before_request"]
# after_request = ["tdn_print_manager.utils.after_request"]

# Job Events
# ----------
# before_job = ["tdn_print_manager.utils.before_job"]
# after_job = ["tdn_print_manager.utils.after_job"]

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
# 	"tdn_print_manager.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

