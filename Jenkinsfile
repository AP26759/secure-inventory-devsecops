pipeline {
    agent any
    options {
        timestamps()
    }
    environment {
        VENV = "${WORKSPACE}/.venv"
        ZAP_HOST = 'http://ccse-zap:8090'
        TARGET_URL = 'http://ccse-jenkins:5000'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Python Setup') {
            steps {
                sh '''
                    set -e
                    echo "Setting up Python environment..."
                    python3 --version
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -U pip
                    pip install -r requirements.txt
                    echo "Python environment ready."
                '''
            }
        }
        stage('SAST - SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=flask-library-api \
                            -Dsonar.projectName='Flask Library API' \
                            -Dsonar.sources=. \
                            -Dsonar.language=py \
                            -Dsonar.python.version=3 \
                            -Dsonar.exclusions=**/ims-frontend/**,**/.venv/**,**/venv/**,**/node_modules/**,**/*.min.js,**/*.min.css,**/Jenkinsfile,**/*.html,**/*.groovy
                        """
                    }
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: false
                }
            }
        }
        stage('Start Flask App') {
            steps {
                sh '''
                    set -e
                    . .venv/bin/activate
                    echo "Starting Flask app for DAST scanning..."
                    export FLASK_ENV=development
                    export JWT_SECRET_KEY=test-secret-key-for-scanning
                    nohup python3 app.py > flask-app.log 2>&1 &
                    echo $! > flask.pid
                    echo "Waiting for Flask to start..."
                    sleep 15
                    echo "Checking if Flask is running..."
                    curl -s http://localhost:5000 || true
                    echo "Flask app started."
                '''
            }
        }
        stage('DAST - OWASP ZAP Scan') {
            steps {
                sh '''
                    set -e
                    mkdir -p reports

                    echo "Running ZAP spider first..."
                    curl -s "http://ccse-zap:8090/JSON/spider/action/scan/?url=http://ccse-jenkins:5000&recurse=true" || true

                    echo "Waiting for spider to complete..."
                    sleep 30

                    echo "Running ZAP active scan..."
                    curl -s "http://ccse-zap:8090/JSON/ascan/action/scan/?url=http://ccse-jenkins:5000&recurse=true" || true

                    echo "Waiting for active scan to complete..."
                    sleep 60

                    echo "Retrieving ZAP alerts..."
                    curl -s "http://ccse-zap:8090/JSON/core/view/alerts/" -o reports/zap-alerts.json || true
                    curl -s "http://ccse-zap:8090/OTHER/core/other/htmlreport/" -o reports/zap-report.html || true

                    echo "ZAP scan complete."
                '''
            }
        }
        stage('Stop Flask App') {
            steps {
                sh '''
                    if [ -f flask.pid ]; then
                        echo "Stopping Flask app..."
                        kill $(cat flask.pid) || true
                        rm flask.pid
                    fi
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'reports/**',
                           fingerprint: true,
                           allowEmptyArchive: true
            archiveArtifacts artifacts: 'flask-app.log',
                           allowEmptyArchive: true
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed - check console output for details.'
        }
    }
}
