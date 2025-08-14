# Transaction Tracker Backend

## Overview

This is the FastAPI backend for the Transaction Tracker app. It provides endpoints to:
- Get user data and transaction history
- Add new transactions (credit/debit)
- Update transaction categories

Data is stored in AWS DynamoDB.

## How to Use

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   - Create a `.env` file with:
     ```
     AWS_ACCESS_KEY_ID=your_key
     AWS_SECRET_ACCESS_KEY=your_secret
     AWS_REGION=your_region
     DYNAMO_USERS_TABLE=your_table_name
     ```

3. **Run the app:**
   ```
   uvicorn main:app --reload
   ```
   The API will be available at `http://localhost:8000`.

## Endpoints

- `GET /getUser` - Get user and transactions (requires `userId` header)
- `POST /addTransaction` - Add a transaction (requires `userId` header)
- `POST /updateTransactionCategory` - Update a transaction's category (requires `userId` header)

## Assumptions

- Only one user is supported for demo/testing.

## Trade-offs / Shortcuts

- No authentication or user management.
- No pagination or filtering for transaction history for rapid development.
- Minimal error handling for rapid development.