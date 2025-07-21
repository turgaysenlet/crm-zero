import os

from nicegui import ui, app

app.add_static_files("/resources", os.path.join(os.path.dirname(__file__), "../../resources"))


@ui.page("/")
def landing_page():
    ui.label("Welcome to CRM Zero").classes("text-xl font-italic h2")
    ui.run_javascript('document.title = "CRM Zero"')

    ui.image("/resources/crm-zero1.png").style("height: 600px; width: 600px;")

    ui.link("API Console", "/docs").classes("text-xl font-bold")
    ui.link("Create Case", "/ui/create_case").classes("text-xl font-bold")
    ui.link("Create Case Comment", "/ui/create_case_comment").classes("text-xl font-bold")
    ui.link("Workflow Step Editor", "/ui/workflow_step_editor").classes("text-xl font-bold")
