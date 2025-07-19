import logging

from pydantic import BaseModel
import requests
import json

from src.core.access.access_rule import AccessRule
from src.core.access.access_type import AccessType
from src.core.access.profile import Profile
from src.core.access.user import User
from src.core.base.data_object import DataObject
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.core.reference.object_reference import ObjectReference
from src.core.reference.object_reference_list import ObjectReferenceList

logging.basicConfig()
logger = logging.getLogger("N8n")
logger.setLevel(logging.DEBUG)


class N8n(BaseModel):
    url: str = "http://localhost:5678/webhook/"
    workflow: str = "case"

    def run_workflow(self, sender: DataObject, message: str):
        full_url: str = self.url + self.workflow
        data = {
            'sender': sender.model_dump(),
            'message': message
        }
        logger.debug(f"URL: {full_url} - Request: {data}")
        response = requests.post(full_url, data=json.dumps(data, default=str),
                                 headers={'Content-Type': 'application/json'})
        logger.info(f"URL: {full_url} - Response: {response.content}")


# For local testing
if __name__ == "__main__":
    account_full_access: AccessRule = AccessRule(
        data_object_type="Account",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    case_full_access: AccessRule = AccessRule(
        data_object_type="Case",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    case_comment_full_access: AccessRule = AccessRule(
        data_object_type="CaseComment",
        access_type=AccessType.READ | AccessType.WRITE | AccessType.CREATE | AccessType.DELETE)
    administrator_profile: Profile = Profile(name="Administrator", access_rules=[account_full_access, case_full_access,
                                                                                 case_comment_full_access])
    support_agent_profile: Profile = Profile(name="Support Agent",
                                             access_rules=[case_full_access, case_comment_full_access])
    sales_agent_profile: Profile = Profile(name="Sales Agent", access_rules=[])
    administrator1: User = User(username="admin", fullname="Administrator",
                                profile_ids=ObjectReferenceList.from_list([administrator_profile]))

    account1: Account = Account(account_name="Account 1",
                                owner_id=ObjectReference.from_object(administrator1),
                                description="Account 1 - Description")
    case1: Case = Case(owner_id=ObjectReference.from_object(administrator1),
                       account_id=ObjectReference.from_object(account1),
                       summary="Where to enter medical details in a personal injure case",
                       description=
                       "I have a personal injure case that I need to enter the medical details into. "
                       "Which document do I enter these details to, like medical expenses, recovery times, etc.?")

    case2: Case = Case(owner_id=ObjectReference.from_object(administrator1),
                       account_id=ObjectReference.from_object(account1),
                       summary="How to file a complaint",
                       description=
                       "I was in an accident, but forgot to report it. Please help me! "
                       "How do I file a complaint to other parties involved in the accident?")

    n8n: N8n = N8n(workflow="case-record-and-suggest-solution")
    n8n.run_workflow(case1, "")
    n8n.run_workflow(case2, "")
    n8n_test: N8n = N8n(workflow="case-record-and-suggest-solution-with-lookup", url="http://localhost:5678/webhook-test/")
    n8n_test.run_workflow(case1, "")