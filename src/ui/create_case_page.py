import uuid
from nicegui import ui


@ui.page("/ui/create_case")
def create_case_page():
    # Workaround to make sure textarea height and resizer area height always matches.
    # Otherwise, resizer area height is fixed at 113px, regardless of textarea height.
    ui.add_head_html('''
        <style>
            .no-resize-textarea textarea {
                resize: none !important;
                field-sizing: content;                
            }
            .no-resize-textarea .q-field__control {
                height: auto !important;
            }
        </style>
    ''')
    ui.label("Create Case").classes("text-xl font-bold")
    ui.run_javascript('document.title = "Create Case"')
    current_user = ['']
    current_account = ['']

    async def create_case():
        ui.notify(f"Creating case for user {current_user[0]} account {current_account[0]}...", color="positive")
        await ui.run_javascript(f'''
            fetch("/api/case", {{
                method: "POST",
                headers: {{"Content-Type": "application/json"}},
                body: JSON.stringify({{
                    "owner_id": "{current_user[0]}",
                    "account_id": "{current_account[0]}",
                    "summary": "{summary.value}",
                    "description": "{description.value}"
                }})
            }})
        ''', timeout=5.0)

    with ui.element('div').classes('flex w-full h-screen'):
        # LEFT PANEL - Dropdowns
        with ui.column().classes('w-1/3 p-4 bg-gray-100'):
            ui.label("User and Account Selection").classes("text-xl font-bold")

            user_dropdown = ui.select(options=[], label='Select User').classes('w-full')
            account_dropdown = ui.select(options=[], label='Select Account').classes('w-full')

            def user_changed(e):
                sp = e.args['label'].split(" | ")
                user_label.text = sp[1]  # show username
                current_user[0] = sp[0]  # store ID

            def account_changed(e):
                sp = e.args['label'].split(" | ")
                account_label.text = sp[1]   # show account number
                current_account[0] = sp[0]   # store ID

            user_dropdown.on('update:model-value', user_changed)
            account_dropdown.on('update:model-value', account_changed)

            async def load_users():
                response = await ui.run_javascript('fetch("/api/users").then(r => r.json())')
                user_dropdown.options = [
                    f'{user["id"]} | {user["username"]}' for user in response
                ]
                user_dropdown.value = user_dropdown.options[0] if user_dropdown.options else ''
                if user_dropdown.options:
                    sp = user_dropdown.value.split(" | ")
                    user_label.text = sp[1]  # show username
                    current_user[0] = sp[0]  # store ID

            async def load_accounts():
                response = await ui.run_javascript('fetch("/api/accounts").then(r => r.json())')
                account_dropdown.options = [
                    f'{acc["id"]} | {acc["account_number"]}' for acc in response
                ]
                account_dropdown.value = account_dropdown.options[0] if account_dropdown.options else ''
                if account_dropdown.options:
                    sp = account_dropdown.value.split(" | ")
                    account_label.text = sp[1]  # show account number
                    current_account[0] = sp[0]  # store ID

            ui.timer(0.1, load_users, once=True)
            ui.timer(0.2, load_accounts, once=True)

        # RIGHT PANEL - Case Details
        with ui.column().classes('w-2/3 p-4 bg-gray-100 h-full'):
            ui.label("Case Details").classes("text-2xl font-bold mb-4")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("User").classes("text-md font-medium").style("width: 64px; ")
                user_label = ui.label("").classes("bg-gray-200 w-full").style("width: 228px; ")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("Account").classes("text-md font-medium").style("width: 64px; ")
                account_label = ui.label("").classes("bg-gray-200 w-full").style("width: 228px; ")

            with ui.column().classes("w-full mb-4"):
                ui.label("Summary").classes("text-md font-medium")
                summary = ui.textarea().classes("w-full bg-gray-200 no-resize-textarea")

            with ui.column().classes("w-full mb-4"):
                ui.label("Description").classes("text-md font-medium")
                description = ui.textarea().classes("w-full bg-gray-200 no-resize-textarea")

            ui.button("Create Case", on_click=create_case)
