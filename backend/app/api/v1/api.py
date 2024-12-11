from fastapi import APIRouter
from app.api.v1.endpoints import users, auth, transactions, accounts, admin, reports, insights, budgets, investments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(insights.router, prefix="/insights", tags=["insights"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
