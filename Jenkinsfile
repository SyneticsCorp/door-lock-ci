// @file Jenkinsfile
// @brief Classroom Red/Green/Gate pipeline; the SCM job performs checkout automatically.
def runPython(String arguments) {
    if (isUnix()) {
        sh ".venv/bin/python ${arguments}"
    } else {
        bat ".venv\\Scripts\\python.exe ${arguments}"
    }
}

pipeline {
    agent any
    options { disableConcurrentBuilds(); timestamps() }
    triggers { pollSCM('H/2 * * * *') }
    stages {
        stage('Setup') {
            steps {
                dir('reports') { deleteDir() }
                script {
                    if (isUnix()) { sh 'python3 -m venv .venv' }
                    else { bat 'python -m venv .venv' }
                    runPython('-m pip install -r requirements.txt')
                }
            }
        }
        stage('Unit Test') {
            steps { script { runPython('-m pytest --junitxml=reports/junit.xml') } }
        }
        stage('Static Analysis') {
            steps { script {
                runPython('-m flake8 doorlock tests --format=pylint --output-file=reports/flake8.txt --exit-zero')
            } }
        }
        stage('Complexity') {
            steps { script { runPython('scripts/ci.py complexity') } }
        }
    }
    post {
        always {
            script {
                if (fileExists('reports/junit.xml')) {
                    junit testResults: 'reports/junit.xml', allowEmptyResults: false
                }
                if (fileExists('reports/flake8.txt')) {
                    recordIssues enabledForFailure: true, failOnError: true,
                        tool: flake8(pattern: 'reports/flake8.txt'),
                        qualityGates: [[threshold: 1, type: 'TOTAL', criticality: 'FAILURE']]
                }
            }
            archiveArtifacts artifacts: 'reports/*', allowEmptyArchive: true
        }
    }
}

