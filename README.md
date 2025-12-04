# 🚀 RAG Chatbot — AWS Deployment (ECS + ALB + DynamoDB + CI/CD + ECR)

![Architecture Overview](image/rag-chatbot-result.png)

Source in document:

![Architecture Diagram](image/source.png)

Store in DynamoDB:
![Architecture Diagram](image/db.png)

This project provides a complete **end-to-end pipeline** for deploying a **RAG (Retrieval-Augmented Generation) chatbot** on AWS:

- Streamlit Frontend (Fargate / ECS)
- FastAPI Backend (Fargate / ECS)
- ALB (Application Load Balancer)
- Private subnets with NAT Gateway
- DynamoDB for query logs
- Chroma for knowledge documents
- ECR for Docker image storage
- GitHub Actions CI/CD

---

# 📁 Project Structure

```
├── frontend/           # Streamlit UI
├── backend/            # FastAPI server with LangChain RAG
├── .github/workflows/  # CI/CD pipelines
├── rag-chatbot-backend-task-def.json
├── rag-chatbot-frontend-task-def.json
└── README.md
```

---

## 💻 Local Setup

### 1. Create Virtual Environment & Install Dependencies
```bash
# Install Requirements
  python -m venv venv
  venv\Scripts\activate   # Windows
  # source venv/bin/activate  # Linux/Mac
  cd backend
  pip install -r requirements.txt


# Building the Vector DB
  backend> python -m populate_database

  ( After finishing that, will show :  ✅ All documents processed and added to Chroma DB. )


# Run the App
  python -m src.rag_app.query_rag

  The response is:
  Answer the question based on the above context: How much does a landing page cost to develop?
  
  ✅ Response: According to the context provided, the cost of a landing page service offered by Galaxy Design Agency is $4,820.
  ✅ Sources: ['D:\\PythonProject\\rag-chatbot-to-aws\\image\\src\\data\\source\\Samsung\\galaxy-design-client-guide.pdf:1:0', 'D:\\PythonProject\\rag-chatbot-to-aws\\backend\\src\\data\\source\\Samsung\\galaxy-design-client-guide.pdf:1:0', 'D:\\PythonProject\\rag-chatbot-to-aws\\image\\src\\data\\source\\Samsung\\galaxy-design-client-guide.pdf:7:0']


# Start FastAPI Server
  python -m src.app_api_handler
  
  ( Visit: http://127.0.0.1:8000/ → should see {"Hello":"World"} )

# Optional: Docker Compose
  docker-compose up -d --build

  (Frontend URL: http://localhost:8501)
```

---

# 🧩 Architecture Overview

### 🔹 Frontend

* Deployed in **public subnet**
* Accessible via **ALB**
* Communicates with backend via internal URL

### 🔹 Backend

* Runs in **private subnets**
* Accesses **Amazon ECR** via NAT Gateway
* Reads knowledge data from S3
* Writes chat logs to DynamoDB

### 🔹 Networking

* Public Subnet → ALB
* Private Subnet → Backend Tasks + NAT Gateway
* Route tables configured for NAT + local VPC

### 🔹 CI/CD

* GitHub Actions automates:

  * Docker build
  * Push to ECR
  * ECS service deployment

---

# 🛠️ Prerequisites

Before deploying, ensure you have:

* AWS Account & IAM user with required permissions
* AWS CLI installed
* GitHub repository with secrets configured:

  * `AWS_ACCOUNT_ID`
  * `AWS_ACCESS_KEY_ID`
  * `AWS_SECRET_ACCESS_KEY`
  * `AWS_REGION`
  * `FRONTEND_REPO`
  * `BACKEND_REPO`
  * `FRONTEND_SERVICE`
  * `BACKEND_SERVICE`
  * `CLUSTER`
  * `FRONTEND_CONTAINER`
  * `BACKEND_CONTAINER`
  
---

# 🏗️ Deployment Steps

## ① Create ECR in AWS

* rag-chatbot-frontend, rag-chatbot-backend


## ② Set Github Secrets

* AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, FASTAPI_URL --->http://<dns.name>

## ③ Create VPC & Subnets

* Public + Private Subnets
* Configure Route Table for NAT

## ④ Security Group && Target Group

* ALB: HTTP 80
* Backend: TCP 8000
* Frontend: TCP 8501

## ⑤ Create ALB

* Internet-facing, assign security group
* Listener rules: /api/* → backend, default → frontend

## ⑥ Deploy ECS Services

* Create cluster, task definitions, and ECS services
* Port mapping: frontend 8501, backend 8000

---

# ⚙️ GitHub Actions Deployment

Enter  project path:
```
  git init
  git add .
  gti commit -m "Intial commit"
  git remote add origin https://github.com/YourUsername/rag-chatbot-aws.git
  git branch -M main
  [git tag v1.0.0.0]
  git push origin main
```

Future Code Update Workflow (No Manual Versioning Needed)
From now on, you only need to run:
```
git add .
git commit -m "Fix bugs or add features"
git push origin main
```

The CI/CD pipeline will automatically:
1. Check the latest tag (e.g., v1.0.0 → v1.0.1)
2. Generate a new version tag
3. Build the Docker image and push it to ECR
4. Update the ECS task definition
5. Perform a rolling deployment of the ECS service

---

# 🗄️ DynamoDB Schema

Table Name: `rag`

* Partition Key: `query_id (string)`


Attributes stored: `query_id`, `create_time`, `query_text`, `answer_text`, `sources`

---

# 🧪 Health Check Endpoints

* Backend: `GET /health  → 200 OK`
* Frontend: `GET /  → 200 OK`

---

# 🛑 Stopping the App (Avoid AWS Charges)

To avoid AWS charges:

* Set **ECS Tasks = 0**
* Delete **NAT Gateway**
* Delete **ALB**
* Release **Elastic IP** used by NAT Gateway

---

# 🧩 Troubleshooting

### 🔥 Cannot pull image from ECR

* NAT Gateway missing
* Wrong route table for private subnet
* ECS task execution role missing:

  * `AmazonECSTaskExecutionRolePolicy`
  * `ecsTaskRole` missing `AmazonBedrockFullAccess` and `AmazonDynamoDBFullAccess`
