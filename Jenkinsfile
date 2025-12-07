pipeline {
    agent any

    environment {
        // TODO: Replace these with your actual registry and credential IDs
        DOCKER_REGISTRY = 'your-docker-registry' // e.g., docker.io/username or gcr.io/project-id
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/maestro-backend"
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/maestro-frontend"
        
        // Jenkins Credentials IDs
        // DOCKER_CREDS_ID = 'docker-registry-credentials-id' // Not used for unauthenticated registries
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

        // Stage 'Push Images' skipped for local deployment

        stage('Deploy to K8s') {
            steps {
                script {
                    echo 'Deploying to Kubernetes...'
                    
                    // Update image tags in k8s manifests to use the specific build tag
                    // Note: This uses Linux sed syntax. For macOS locally, use sed -i '' ...
                    sh "sed -i 's|image: .*maestro-backend.*|image: ${BACKEND_IMAGE}:${BUILD_NUMBER}|' k8s/backend.yaml"
                    sh "sed -i 's|image: .*maestro-frontend.*|image: ${FRONTEND_IMAGE}:${BUILD_NUMBER}|' k8s/frontend.yaml"

                    // Using withKubeConfig from Kubernetes CLI Plugin
                    withKubeConfig([credentialsId: KUBE_CONFIG_ID]) {
                        // Create/Update Secret safely
                        // Ensure you have created a 'Secret text' credential in Jenkins with ID 'google-api-key'
                        withCredentials([string(credentialsId: 'google-api-key', variable: 'GOOGLE_API_KEY')]) {
                            sh """
                                kubectl create secret generic maestro-secrets \
                                --from-literal=GOOGLE_API_KEY=\${GOOGLE_API_KEY} \
                                --dry-run=client -o yaml | kubectl apply --validate=false -f -
                            """
                        }

                        sh 'kubectl apply  -f k8s/backend.yaml'
                        sh 'kubectl apply  -f k8s/frontend.yaml'
                    }
                    
                    // Optional: Force rollout restart to ensure new pods are picked up if using 'latest' tag previously
                    // sh 'kubectl rollout restart deployment/backend'
                    // sh 'kubectl rollout restart deployment/frontend'
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo 'Verifying Deployment...'
                    
                    withKubeConfig([credentialsId: KUBE_CONFIG_ID]) {
                        // Wait for rollout to complete
                        timeout(time: 2, unit: 'MINUTES') {
                            sh 'kubectl rollout status deployment/backend'
                            sh 'kubectl rollout status deployment/frontend'
                        }

                        // Port Forwarding Example for Verification
                        // This runs port-forward in the background, checks the endpoint, and then cleans up.
                        // Note: This assumes the Jenkins agent can bind to port 8000.
                        echo 'Starting port-forward for health check...'
                        sh """
                            # Start port-forward in background
                            kubectl port-forward service/backend-service 8000:8000 &
                            PF_PID=\$!
                            
                            # Wait for connection to be established
                            sleep 5
                            
                            # Check health (assuming /health or root endpoint exists, adjust as needed)
                            # Using || true to prevent pipeline failure if just testing connectivity logic
                            curl -v http://localhost:8000/ || echo "Could not connect to backend"
                            
                            # Kill the port-forward process
                            kill \$PF_PID
                        """
                    }
                }
            }
        }
    }
    

}
