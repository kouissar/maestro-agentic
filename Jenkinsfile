pipeline {
    agent any

    environment {
        // TODO: Replace these with your actual registry and credential IDs
        DOCKER_REGISTRY = 'your-docker-registry' // e.g., docker.io/username or gcr.io/project-id
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/maestro-backend"
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/maestro-frontend"
        
        // Jenkins Credentials IDs
        DOCKER_CREDS_ID = 'docker-registry-credentials-id'
        KUBE_CONFIG_ID = 'k8s-kubeconfig'
    }

    stages {
        stage('Build Backend') {
            steps {
                script {
                    echo 'Building Backend Image...'
                    docker.build("${BACKEND_IMAGE}:${BUILD_NUMBER}", "-f Dockerfile .")
                }
            }
        }

        stage('Build Frontend') {
            steps {
                script {
                    echo 'Building Frontend Image...'
                    docker.build("${FRONTEND_IMAGE}:${BUILD_NUMBER}", "-f web_ui/Dockerfile web_ui")
                }
            }
        }

        stage('Push Images') {
            steps {
                script {
                    echo 'Pushing Images to Registry...'
                    docker.withRegistry("https://${DOCKER_REGISTRY}", DOCKER_CREDS_ID) {
                        
                        // Push Backend
                        docker.image("${BACKEND_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${BACKEND_IMAGE}:${BUILD_NUMBER}").push('latest')
                        
                        // Push Frontend
                        docker.image("${FRONTEND_IMAGE}:${BUILD_NUMBER}").push()
                        docker.image("${FRONTEND_IMAGE}:${BUILD_NUMBER}").push('latest')
                    }
                }
            }
        }

        stage('Deploy to K8s') {
            steps {
                script {
                    echo 'Deploying to Kubernetes...'
                    
                    // Update image tags in k8s manifests to use the specific build tag
                    // Note: This uses Linux sed syntax. For macOS locally, use sed -i '' ...
                    sh "sed -i 's|image: .*maestro-backend.*|image: ${BACKEND_IMAGE}:${BUILD_NUMBER}|' k8s/backend.yaml"
                    sh "sed -i 's|image: .*maestro-frontend.*|image: ${FRONTEND_IMAGE}:${BUILD_NUMBER}|' k8s/frontend.yaml"

                    withKubeConfig([credentialsId: KUBE_CONFIG_ID]) {
                        sh 'kubectl apply -f k8s/backend.yaml'
                        sh 'kubectl apply -f k8s/frontend.yaml'
                        
                        // Optional: Force rollout restart to ensure new pods are picked up if using 'latest' tag previously
                        // sh 'kubectl rollout restart deployment/backend'
                        // sh 'kubectl rollout restart deployment/frontend'
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up docker images to save space
            sh "docker rmi ${BACKEND_IMAGE}:${BUILD_NUMBER} || true"
            sh "docker rmi ${FRONTEND_IMAGE}:${BUILD_NUMBER} || true"
        }
    }
}
