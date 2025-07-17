# crm-zero
CRM Zero - Simple CRM implementation in Python

Main Features
- Standard objects
  - Account
  - Case
  - Case Comment
  - Workflow
  - Workflow Trigger
  - Workflow Step - Code in Python
- Access Objects
  - Access Profile
  - Access Rule
  - User
- Functionality
  - Reference objects and reference lists for decoupling object relationships 
  - Working Workflows with running live workflow code on object triggers with user generated workflow code in Python 
- Database
  - Database type: SQLLite3 -Local file based database
  - Tables: Account, Case, CaseComment, User, Profile, Workflow, WorkflowTrigger, WorkflowStep
- API Server
  - Access to standard objects
  - LIST: accounts, cases, case_comments, users, workflow, workflow_steps
  - LIST: with access control: accounts, cases - via user permission roles
  - GET: account, case, user, workflow, workflow_step
- UI Pages
  - Case Creation page
  - Case Comment Creation page
  - Wrokflow Step Code Editor (Python) page 