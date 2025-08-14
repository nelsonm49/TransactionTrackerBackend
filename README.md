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

## Deploying to AWS EC2 (Amazon Linux, with dnf, git, and systemd)

### 1. Launch an EC2 Instance
- Use Amazon Linux 2.
- Open ports 22 (SSH) and 80 in the security group.

### 2. Connect to Your Instance
```sh
ssh ec2-user@<your-ec2-public-dns>
```

### 3. Install Dependencies (using dnf)
```sh
sudo dnf update -y
sudo dnf install -y python3 python3-pip git
```

### 4. Clone Your Repository & Set Up Python Environment
```sh
git clone <your-repo-url>
cd TransactionTracker
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn boto3 python-dotenv
```

### 5. Set Environment Variables
- Create a `.env` file in the backend directory with your AWS and DynamoDB credentials.

### 6. Run the FastAPI App with systemd (on port 80)

1. **Create a systemd service file:**

   ```sh
   sudo nano /etc/systemd/system/transaction-backend.service
   ```

   Paste the following (update paths as needed):

   ```
   [Unit]
   Description=Transaction Tracker FastAPI Backend
   After=network.target

   [Service]
   WorkingDirectory=/home/ec2-user/TransactionTrackerBackend
   Environment="PATH=/home/ec2-user/TransactionTrackerBackend/venv/bin"
   ExecStart=/home/ec2-user/TransactionTrackerBackend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 80
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Reload systemd and start the service:**
   ```sh
   sudo systemctl daemon-reload
   sudo systemctl start transaction-backend
   sudo systemctl enable transaction-backend
   ```

3. **Check the status of your service:**
   ```sh
   sudo systemctl status transaction-backend
   ```

4. **View live logs:**
   ```sh
   sudo journalctl -u transaction-backend -f
   ```

- The API will be available at `http://<your-ec2-public-dns>/`

### 7. Updating Your Code
- To update, SSH into your instance, pull the latest code, and restart pm2:
```sh
cd TransactionTrackerBackend
git pull
pm2 restart transaction-backend
```