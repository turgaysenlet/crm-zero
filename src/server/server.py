from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List
import uvicorn

from src.api.account_api_record import AccountApiRecord
from src.api.case_api_record import CaseApiRecord
from src.api.user_api_record import UserApiRecord
from src.core.access.user import User
from src.core.objects.account import Account
from src.core.objects.case import Case
from src.db.account_record import AccountRecord
from src.db.case_record import CaseRecord
from src.db.database import Database
from src.db.user_record import UserRecord

app = FastAPI()
router = APIRouter()


class Server:
    db: Database

    def __init__(self):
        self.init_db()
        self.router = APIRouter()
        self.router.add_api_route("/cases", self.get_cases, response_model=List[CaseApiRecord])
        self.router.add_api_route("/accounts", self.get_accounts, response_model=List[AccountApiRecord])
        self.router.add_api_route("/users", self.get_users, response_model=List[UserApiRecord])
        self.router.add_api_route("/cases_by_username", self.get_cases_by_username, response_model=List[CaseApiRecord])

    def init_db(self):
        # Connect to database
        self.db = Database(db_name="database/crm.db")
        # db.delete_if_exists()
        self.db.init_db_schema()
        self.db.connect()

    async def get_cases(self) -> List[CaseApiRecord]:
        username = "admin"
        user_records: List[UserRecord] = self.db.read_objects(UserRecord.table_name(), "User", None)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user = next((u for u in users if u.username == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            case_records: List[CaseRecord] = self.db.read_objects(CaseRecord.table_name(), "Case", user)
            cases: List[Case] = [case_record.convert_to_object() for case_record in case_records]
            case_api_records: List[CaseApiRecord] = [CaseApiRecord.from_object(_case) for _case in cases]
            if not case_api_records:
                raise HTTPException(status_code=404, detail=f"No cases found.")
            return case_api_records

    async def get_accounts(self) -> List[AccountApiRecord]:
        username = "admin"
        user_records: List[UserRecord] = self.db.read_objects(UserRecord.table_name(), "User", None)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user = next((u for u in users if u.username == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            account_records: List[AccountRecord] = self.db.read_objects(AccountRecord.table_name(), "Account", user)
            accounts: List[Account] = [account_record.convert_to_object() for account_record in account_records]
            account_api_records: List[AccountApiRecord] = [AccountApiRecord.from_object(account) for account in accounts]
            if not account_api_records:
                raise HTTPException(status_code=404, detail=f"No account found.")
        return account_api_records

    async def get_users(self) -> List[UserApiRecord]:
        user_records: List[UserRecord] = self.db.read_objects(UserRecord.table_name(), "User", None)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user_api_records: List[UserApiRecord] = [UserApiRecord.from_object(user) for user in users]
        if not user_api_records:
            raise HTTPException(status_code=404, detail=f"No users found.")
        return user_api_records

    async def get_cases_by_username(self, username: str = Query(..., description="Username to filter cases by")) -> \
            List[CaseApiRecord]:
        user_records: List[UserRecord] = self.db.read_objects(UserRecord.table_name(), "User", None)
        users: List[User] = [user_record.convert_to_object() for user_record in user_records]
        user = next((u for u in users if u.username == username), None)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found.")
        else:
            case_records: List[CaseRecord] = self.db.read_objects(CaseRecord.table_name(), "Case", user)
            cases: List[Case] = [case_record.convert_to_object() for case_record in case_records]
            case_api_records: List[CaseApiRecord] = [CaseApiRecord.from_object(_case) for _case in cases]
            # Username based filtering
            # user_cases = [case for case in DUMMY_CASES if case.owner_id == username]
            if not case_api_records:
                raise HTTPException(status_code=404, detail=f"No cases found for user '{username}'.")
            return case_api_records


# Mount the router
server = Server()
app.include_router(server.router)

# To run:
if __name__ == "__main__":
    uvicorn.run("src.server.server:app", reload=True)
