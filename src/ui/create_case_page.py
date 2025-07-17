import uuid
from nicegui import ui


@ui.page("/ui/create_case")
def create_case_page():
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
        with ui.column().classes('w-1/2 p-4 bg-gray-100'):
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
        with ui.column().classes('w-1/2 p-4 bg-gray-100 h-full'):
            ui.label("Case Details").classes("text-2xl font-bold mb-4")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("User").classes("w-24")
                user_label = ui.label("").classes("bg-gray-200 w-full")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("Account").classes("w-24")
                account_label = ui.label("").classes("bg-gray-200 w-full")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("Summary").classes("w-24")
                summary = ui.input().classes("bg-gray-200 w-full")

            with ui.row().classes("items-start gap-2 mb-4"):
                ui.label("Description").classes("w-24 pt-1")
                description = ui.textarea().classes("bg-gray-200 w-full h-32")

            ui.button("Create Case", on_click=create_case)
