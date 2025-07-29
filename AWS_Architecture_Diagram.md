# Quiz App AWS Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud (us-east-1)                    │
│                                                                 │
│  ┌─────────────────┐                 ┌─────────────────────────┐ │
│  │   Internet      │                 │      CloudWatch         │ │
│  │   Gateway       │                 │   - CPU Alarms          │ │
│  │                 │                 │   - Monitoring          │ │
│  └─────────────────┘                 └─────────────────────────┘ │
│           │                                                     │
│           │                                                     │
│  ┌─────────────────┐                                           │
│  │  Default VPC    │                                           │
│  │                 │                                           │
│  │  ┌─────────────────────────────────────────────────────┐   │ │
│  │  │              Public Subnet                          │   │ │
│  │  │                                                     │   │ │
│  │  │  ┌─────────────────┐    ┌─────────────────────────┐ │   │ │
│  │  │  │   EC2 Instance  │    │    Security Groups      │ │   │ │
│  │  │  │                 │    │                         │ │   │ │
│  │  │  │ quiz-app-server │    │  quiz-app-sg:           │ │   │ │
│  │  │  │   (t3.micro)    │    │  - SSH (22)             │ │   │ │
│  │  │  │                 │    │  - HTTP (80)            │ │   │ │
│  │  │  │ Flask App       │    │  - HTTPS (443)          │ │   │ │
│  │  │  │ Python 3.9      │    │  - Custom (5000)        │ │   │ │
│  │  │  │ Systemd Service │    │                         │ │   │ │
│  │  │  └─────────────────┘    └─────────────────────────┘ │   │ │
│  │  │           │                                         │   │ │
│  │  └───────────│─────────────────────────────────────────┘   │ │
│  │              │                                             │ │
│  │              │ MySQL Connection                            │ │
│  │              │ (Port 3306)                                 │ │
│  │              │                                             │ │
│  │  ┌───────────▼─────────────────────────────────────────┐   │ │
│  │  │              Private Subnet                         │   │ │
│  │  │                                                     │   │ │
│  │  │  ┌─────────────────┐    ┌─────────────────────────┐ │   │ │
│  │  │  │   RDS MySQL     │    │    Security Groups      │ │   │ │
│  │  │  │                 │    │                         │ │   │ │
│  │  │  │  quiz-app-db    │    │  quiz-db-sg:            │ │   │ │
│  │  │  │  (db.t3.micro)  │    │  - MySQL (3306)         │ │   │ │
│  │  │  │                 │    │    from quiz-app-sg     │ │   │ │
│  │  │  │ Database:       │    │  - MySQL (3306)         │ │   │ │
│  │  │  │  quiz_app       │    │    from your IP         │ │   │ │
│  │  │  │                 │    │                         │ │   │ │
│  │  │  │ Auto Backup     │    │                         │ │   │ │
│  │  │  │ (7 days)        │    │                         │ │   │ │
│  │  │  └─────────────────┘    └─────────────────────────┘ │   │ │
│  │  └─────────────────────────────────────────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

External Access:
User → Internet → EC2 Public IP:5000 → Flask App → RDS MySQL
```

## Component Details:

### EC2 Instance (quiz-app-server)
- **Type**: t3.micro (Free Tier)
- **OS**: Amazon Linux 2023
- **Public IP**: ec2-50-16-51-76.compute-1.amazonaws.com
- **Application**: Flask Quiz App (Python 3.9)
- **Service**: Systemd auto-start service

### RDS Database (quiz-app-db)
- **Type**: db.t3.micro (Free Tier)
- **Engine**: MySQL 8.0
- **Database**: quiz_app
- **Endpoint**: quiz-app-db.cuxqgu8w4uxp.us-east-1.rds.amazonaws.com
- **Backup**: 7-day retention

### Security Configuration
- **EC2 Security Group**: Allows HTTP, HTTPS, SSH, and port 5000
- **RDS Security Group**: Allows MySQL access from EC2 and admin IP
- **Network**: Default VPC with public subnet for EC2

### Monitoring & Backup
- **CloudWatch**: CPU monitoring alarms for EC2 and RDS
- **RDS Backup**: Automatic daily backups with 7-day retention