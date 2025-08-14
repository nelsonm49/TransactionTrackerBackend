from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
import os
import time
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables from .env
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
DYNAMO_USERS_TABLE = os.getenv("DYNAMO_USERS_TABLE")

# Initialize DynamoDB client
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
userTable = dynamodb.Table(DYNAMO_USERS_TABLE)

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class TransactionRequest(BaseModel):
    type: str
    amount: float
    category: str = None

class UpdateCategoryRequest(BaseModel):
    transactionId: str
    category: str

@app.get("/getUser")
def get_user(userId: str = Header(...)):
    try:
        response = userTable.get_item(Key={"user_id": userId})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="User not found")
        user = response["Item"]
        # Sort transactions by date_created descending (most recent first)
        transactions = user.get("transactions", [])
        transactions.sort(key=lambda tx: tx.get("date_created", 0), reverse=True)
        user["transactions"] = transactions
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=getattr(e, "detail", str(e)))

@app.post("/addTransaction")
def add_transaction(req: TransactionRequest, userId: str = Header(...)):
    try:
        # Fetch user
        response = userTable.get_item(Key={"user_id": userId})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="User not found")
        user = response["Item"]

        # Prepare new transaction
        transactions = user.get("transactions", [])
        transaction_id = str(len(transactions))
        wallet_balance = Decimal(str(user.get("wallet_balance", 0)))

        reqAmount = "{:.2f}".format(req.amount)
        amount = Decimal(reqAmount) if req.type.upper() == "CREDIT" else -Decimal(reqAmount)
        new_balance = wallet_balance + amount

        # Check for sufficient funds on DEBIT
        if req.type.upper() == "DEBIT" and wallet_balance < Decimal(reqAmount):
            raise HTTPException(status_code=400, detail="Insufficient funds")

        new_transaction = {
            "transaction_id": transaction_id,
            "amount": Decimal(reqAmount),
            "type": req.type.upper(),
            "category": req.category if req.category else "None",
            "date_created": int(time.time()),
            "balance_after_transaction": Decimal(new_balance),
        }

        # Update transactions and wallet_balance
        transactions.append(new_transaction)
        userTable.update_item(
            Key={"user_id": userId},
            UpdateExpression="SET transactions = :t, wallet_balance = :b",
            ExpressionAttributeValues={
                ":t": transactions,
                ":b": new_balance,
            }
        )

        return {"message": "Transaction added", "transaction": new_transaction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=getattr(e, "detail", str(e)))

@app.post("/updateTransactionCategory")
def update_transaction_category(req: UpdateCategoryRequest, userId: str = Header(...)):
    try:
        # Fetch user
        response = userTable.get_item(Key={"user_id": userId})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="User not found")
        user = response["Item"]

        # Find and update the transaction
        # TODO: expedite using the transaction_id
        transactions = user.get("transactions", [])
        updated = False
        for tx in transactions:
            if str(tx.get("transaction_id")) == str(req.transactionId):
                tx["category"] = req.category
                updated = True
                break

        if not updated:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Update the user in DynamoDB
        userTable.update_item(
            Key={"user_id": userId},
            UpdateExpression="SET transactions = :t",
            ExpressionAttributeValues={
                ":t": transactions,
            }
        )

        return {
            "message": "Transaction category updated",
            "user_id": userId,
            "transaction_id": req.transactionId,
            "category": req.category,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=getattr(e, "detail", str(e)))