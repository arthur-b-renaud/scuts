pipeline {
    agent any

    stages {
        stage ("Code pull"){
            steps{
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh'''
                export PYINT=python3.6
                export PYVERSION=3.6
                "/usr/bin/$PYINT" -c 'from virtualenv import create_environment;create_environment(\"_venv\", site_packages=True)'

                export PIPENV_VENV_IN_PROJECT=$WORKSPACE/_venv
                $PYINT -m pip install pipenv
                $PYINT -m pipenv --python $PYVERSION
                $PYINT -m pipenv install --skip-lock

                PYPIPENVEXEC="$($PYINT -m pipenv --venv)/bin/python$PYVERSION"
                echo $PYPIPENVEXEC
                '''

                sh './ressources/scripts/opencv.sh'

                sh '''
                export PYINT=python3.6
                export PYVERSION=3.6
                PYPIPENVLOC="$($PYINT -m pipenv --venv)"
                ln -s "/usr/local/lib/python3.5/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so" "$PYPIPENVLOC/lib/python3.6/site-packages/cv2/cv2.so"
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Testing'
                sh '''
                export PYINT=python3.6
                export PYVERSION=3.6

                export PIPENV_VENV_IN_PROJECT=$WORKSPACE/_venv
                PYPIPENVEXEC="$($PYINT -m pipenv --venv)/bin/python$PYVERSION"

                echo $PYPIPENVEXEC
                echo "Sending pytest"

                $PYPIPENVEXEC -m pytest
                '''
                echo 'End Testing'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying'
            }
        }
    }
    post {
        always {
            echo 'This will always run'

        }
        success {
            echo 'This will run only if successful'
        }
        failure {
            echo 'This will run only if failed'
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}