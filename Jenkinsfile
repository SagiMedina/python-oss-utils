@Library('miil-shared-libraries@master') _
miilPipeline {
    masterLabel = "cn-cpu" // Node label of machine who will run the pipeline (master)
    slaveLabel = "cn" // Node label of machines who will run the test workload (slaves)

    toxEnvironments = "py36,py37,py38"
    splitCount = 1
    pythonPackages = '.'
    // (optional) if you want to pass a .env file (environment variables) to the Docker container of microservice
     dotEnvFileCredentialsId = "OTS_UTILS_PYTHON_SDK_DOTENV"
}