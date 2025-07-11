import uuid

from nicegui import ui


@ui.page("/ui/create_case_comment")
def create_case_comment_page():
    ui.label("Create Case Comment").classes("text-xl font-bold")
    ui.run_javascript('document.title = "Create Case"')
    current_user = ['']
    current_account = ['']

    async def create_case():
        print(f"CREATE CASE COMMENT: current_account: {current_account[0]}, current_user: {current_user[0]}, summary: {summary.value}, description: {description.value}")
        response = await ui.run_javascript(f'''
                        fetch("/api/case_comment", {{
                            method: "POST",
                            headers: {{"Content-Type": "application/json"}},
                            body: JSON.stringify({{"owner_id": "{current_user[0]}", 
                            "account_id": "{current_account[0]}", 
                            "summary": "{summary.value}", 
                            "description": "{description.value}"
                            }})
                        }})
                        ''', timeout=5.0)
        ui.notify(f"Creating case comment for user {current_user[0]} account {current_account[0]}...", color="positive")

    with ui.element('div').classes('flex w-full h-screen'):  # force flex container
        with ui.column().classes('w-1/4 p-4 bg-gray-100'):
            ui.label("Users").classes("text-xl font-bold")

            async def load_users():
                response = await ui.run_javascript('fetch("/api/users").then(r => r.json())')
                for wf in response:
                    ui.button(f'{wf["fullname"]} ({wf["username"]})',
                              on_click=lambda _, id=wf["id"], username=wf['username']: load_user_details(id, username)).classes("w-full")

            ui.timer(0.1, load_users, once=True)
        with ui.column().classes('w-1/4 p-4 bg-gray-100'):
            ui.label("Accounts").classes("text-xl font-bold")

            async def load_accounts():
                response = await ui.run_javascript('fetch("/api/accounts").then(r => r.json())')
                for wf in response:
                    ui.button(f'{wf["account_name"]} ({wf["account_number"]})',
                              on_click=lambda _, id=wf["id"], account_number=wf["account_number"]: load_account_details(id, account_number)).classes("w-full")

            ui.timer(0.1, load_accounts, once=True)

        # RIGHT PANEL - Workflow step details
        with ui.column().classes('grow w-2/4 p-4 bg-gray-100 h-full'):
            title = ui.label("Case details").classes("text-2xl font-bold mb-4")

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("User").classes("w-24")
                user = ui.label("user").classes('bg-gray-200 w-full')
            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("Account").classes("w-24")
                account = ui.label("account").classes('bg-gray-200 w-full')

            with ui.row().classes("items-center gap-2 mb-4"):
                ui.label("Summary").classes("w-24")
                summary = ui.input().classes('bg-gray-200 w-full')

            with ui.row().classes("items-start gap-2"):
                ui.label("Description").classes("w-24 pt-1")
                description = ui.textarea().classes('bg-gray-200 w-full h-32')

            ui.button("Save code changes", on_click=create_case)

            async def load_account_details(id: str, account_number: str):
                current_account[0] = id
                account.text = account_number

            async def load_user_details(id: str, username: str):
                current_user[0] = id
                user.text = username
