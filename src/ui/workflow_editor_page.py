import uuid

from nicegui import ui


@ui.page("/ui/workflow_step_editor")
def workflow_editor_page():
    ui.run_javascript('document.title = "Workflow Step Editor"')
    ui.label("Workflow Step Editor").classes("text-xl font-bold")
    current_id = ['']

    with ui.element('div').classes('flex w-full h-screen'):  # force flex container
        # LEFT PANEL - List of workflow steps
        with ui.column().classes('w-1/4 p-4 bg-gray-100'):
            ui.label("Workflow Steps").classes("text-xl font-bold")

            async def load_workflow_steps():
                response = await ui.run_javascript('fetch("/workflow_steps").then(r => r.json())')
                for wf in response:
                    ui.button(wf["workflow_step_name"],
                              on_click=lambda _, id=wf["id"], current_id=id: load_workflow_detail(id)).classes("w-full")

            ui.timer(0.1, load_workflow_steps, once=True)

        # RIGHT PANEL - Workflow step details
        with ui.column().classes('w-3/4 p-4 bg-gray-100'):
            async def save_workflow_code():
                if not current_id[0]:
                    ui.notify("No step selected", color="negative")
                    return
                code = editor.value
                workflow_step_id = str(current_id[0])
                response = await ui.run_javascript(f'''
                fetch("/workflow_step/{workflow_step_id}", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{"id": "{workflow_step_id}", "workflow_step_name": "", "workflow_step_code": {code!r}
                    }})
                }})
                ''', timeout=5.0)
                ui.notify(f"Saving step {current_id[0]}:\n{code[:30]}...", color="positive")


            title = ui.label("Select a workflow step").classes("text-2xl font-bold")
            description = ui.label("").classes("mb-2")
            editor = ui.codemirror(language='Python', value='', theme='vscodeDark').classes("h-96 w-full")
            ui.button("Save code changes", on_click=save_workflow_code)

            async def load_workflow_detail(workflow_step_id: str):
                current_id[0] = workflow_step_id
                response = await ui.run_javascript(f'fetch("/workflow_step/{workflow_step_id}").then(r => r.json())')
                title.set_text(response["workflow_step_name"])
                description.set_text(response["workflow_step_name"])
                editor.set_value(response["workflow_step_code"])
