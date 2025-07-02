from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List
import uvicorn

from src.api.case_api_record import CaseApiRecord
from src.core.access.user import User
from src.core.objects.case import Case
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
        self.router.add_api_route("/cases", self.get_cases_by_username, response_model=List[CaseApiRecord])

    def init_db(self):
        # Connect to database
        self.db = Database(db_name="database/crm.db")
        # db.delete_if_exists()
        self.db.init_db_schema()
        self.db.connect()

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
