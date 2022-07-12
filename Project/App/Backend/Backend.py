from data_analysis.pipeline import data_analysis_pipeline_main
from data_science.pipeline import data_science_pipeline_main
from deployment.pipeline import deployment_pipeline_main
from Requirements import requirements 

from os import listdir, getcwd, chdir, path
from os.path import isfile, join
import shutil
#old paradigm of the app, but serves as an example
def get_envs(method):
    method = method.lower().strip() 
    #TODO
    if method in ['development', 'dev']:
        pass # catch the envs within the config .json file
        #get env variables from the Env folder in the development environment
    elif method in ['production', 'prod']:
        #get env variables from the OS (docker, linux) in the production environment
        env = os.environ.get('ENV').lower().strip()
        deploy = os.environ.get('DEPLOY').lower().strip()
        
    return env, deploy
#Or open the env by the config json file

def transfer_models():
    #get the current working directory
    cwd = getcwd()
    #get the path to the Models folder
    dev_models = path.join(cwd, '..', '..', 'Models', 'Production')
    #get all the files in the Models folder
    prod_models = [f for f in listdir(dev_models) if isfile(join(dev_models, f))]
    #get the path to the Models folder on the current dir
    deploy_models = path.join(cwd, 'Models')
    #create the Models folder on the current dir if it doesn't exist
    if not path.exists(deploy_models):
        os.makedirs(deploy_models)
    #copy all the files from the Models folder two levels above to the Models folder on the current dir
    for file in prod_models:
        shutil.copy(path.join(dev_models, file), path.join(deploy_models, file))
                
def App_main(env_config, deploy_run = False):
    
    current_env, deploy_method = get_envs(env_config)
    
    if current_env in ['development', 'dev']:
        #issue the requirements for the development environment
        requirements()
        #run the data analysis pipeline
        data_analysis_pipeline_main()
        #run the data science pipeline, this includes the collection, cleaning and analysis report issuing
        data_science_pipeline_main()
        #run the deployment pipeline, this includes the train and testing for the models
        #TODO
        transfer_models() #pass some arguments to confirm if we can do it, if the models are approved
        #transfer the models from the development folder to the deployment folder and the app folder
        
        deployment_pipeline_main(deploy_method = deploy_method, deploy_run = deploy_run)
        #run the deployment pipeline, this includes the train and testing for the models
        
        return True
    
    elif current_env in ['production', 'prod']:
        
        deployment_pipeline_main(deploy_method = deploy_method)
        #log the deployment pipeline
    else:
        print("Please specify the environment variable") #substitute with logging
        sys.exit(1)
    
    return True #substitute with logging