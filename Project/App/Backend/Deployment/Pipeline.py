# This file is used to deploy the application to the cloud
# It manages the pipeline orchestrating the deployment process
import os
import sys
import subprocess
# If the environment variable is fastapi, import the fastapi deployment pipeline
# If the environment variable is none of the above, raise an error
def deployment_pipeline_main(deploy_method = None):
    deploy_method = os.environ.get('DEPLOY').lower().strip() if deploy_method is None else deploy_method
    
    if deploy_method in ['fastapi', 'fa', 'fp']:
        
        from Api.Deployment_api import deploy_main
        print("Running FastAPI deployment pipeline") #substitute with logging
        
    else:
        print("Please specify the environment variable") #substitute with logging
        sys.exit(1)
    
    deploy_main()
    return True