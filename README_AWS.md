# Quiz App

A full-stack quiz application built with Flask, MySQL, HTML, CSS, and JavaScript. Now deployed on AWS with scalable infrastructure.

## 🌐 Live Application
**AWS Deployment**: http://ec2-50-16-51-76.compute-1.amazonaws.com:5000

## Features

- User authentication (registration and login)
- Excel upload for question ingestion
- Quiz with a timer and navigation
- Results page displaying the score
- Cloud-based deployment with AWS EC2 and RDS
- Automated monitoring and backup

## Local Development Setup

1. Clone the repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up the MySQL database using the `schema.sql` file.
4. Run the Flask application using `python app.py`.
5. Open your web browser and navigate to `http://localhost:5000`.

## AWS Deployment

### Architecture
The application is deployed on AWS using:
- **EC2 Instance**: t3.micro (Free Tier) running Amazon Linux 2023
- **RDS Database**: MySQL 8.0 on db.t3.micro (Free Tier)
- **CloudWatch**: Monitoring and alarms
- **Security Groups**: Network security configuration

### Quick Deployment

#### Prerequisites
- AWS Free Tier account
- IAM user with EC2, RDS, CloudWatch permissions

#### Automated Deployment
1. Launch EC2 instance (t3.micro, Amazon Linux 2023)
2. Create RDS MySQL instance (db.t3.micro)
3. Configure security groups
4. Run deployment script:
```bash
chmod +x deploy/deployment_script.sh
./deploy/deployment_script.sh
```

#### Manual Deployment
For detailed step-by-step instructions, see: [Manual Deployment Steps](deploy/manual_deployment_steps.md)

### Environment Variables
The application uses environment variables for database configuration:
```bash
export DB_HOST=your-rds-endpoint
export DB_USER=admin
export DB_PASSWORD=your-password
export DB_NAME=quiz_app
```

### Infrastructure Details

#### EC2 Instance
- **Instance Type**: t3.micro (1 vCPU, 1 GB RAM)
- **Operating System**: Amazon Linux 2023
- **Public Access**: Yes (for web application)
- **Security Group**: Allows HTTP (80), HTTPS (443), SSH (22), Custom (5000)

#### RDS Database
- **Engine**: MySQL 8.0
- **Instance Class**: db.t3.micro (1 vCPU, 1 GB RAM)
- **Storage**: 20 GB General Purpose SSD
- **Backup**: 7-day retention period
- **Multi-AZ**: Single-AZ (Free Tier)

#### Monitoring & Backup
- **CloudWatch Alarms**: CPU utilization monitoring for EC2 and RDS
- **RDS Backup**: Automated daily backups with 7-day retention
- **Service Management**: Systemd service for auto-restart

### Security Configuration
- EC2 security group allows web traffic and SSH access
- RDS security group restricts database access to EC2 instance only
- Environment variables used for sensitive configuration
- Database credentials stored securely

### Scaling Considerations
- **Vertical Scaling**: Can upgrade to larger instance types
- **Horizontal Scaling**: Can add Application Load Balancer and multiple EC2 instances
- **Database Scaling**: Can enable Multi-AZ deployment and read replicas

### Cost Optimization
- Uses AWS Free Tier eligible resources
- Automated backup with reasonable retention period
- Single-AZ deployment to minimize costs
- Monitoring to prevent unexpected charges

## Troubleshooting

### Common Issues
1. **Database Connection Error**: Check security groups and RDS endpoint
2. **Service Not Starting**: Check systemd service logs
3. **Web App Not Accessible**: Verify EC2 security group allows port 5000

### Useful Commands
```bash
# Check service status
sudo systemctl status quiz-app.service

# View service logs
sudo journalctl -u quiz-app.service -f

# Restart service
sudo systemctl restart quiz-app.service

# Test database connection
mysql -h [RDS-ENDPOINT] -u admin -p
```

## Project Structure
```
quizXmentor/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
├── templates/            # HTML templates
├── static/              # CSS and JavaScript files
├── deploy/              # Deployment scripts and documentation
│   ├── deployment_script.sh
│   └── manual_deployment_steps.md
├── AWS_Architecture_Diagram.md
└── README.md            # This file
```

## Contributing
Feel free to submit issues and enhancement requests!

## License
This project is open source and available under the [MIT License].