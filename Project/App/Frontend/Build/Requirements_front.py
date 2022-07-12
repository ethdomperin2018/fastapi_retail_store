import os
import sys
import subprocess
from loguru import logger as log

class InvalidEnvorimentError(Exception):
    """
    Exception raised when the environment is not valid
    """
    pass

#TODO make the file name a constant using pydantic library with the freeze decorator

def requirements(task = None, env = None):
    """
    It takes a task as an argument, and if the task is generate, it generates a requirements.front.txt
    file, if the task is update, it updates the requirements.front.txt file, and if the task is install,
    it installs the requirements.front.txt file
    
    :param task: This is the task that you want to perform. It can be generate, update or install
    """
    if task in ['generate','update']:
        
        if task == 'generate': 
            log.info('Generating requirements ...')
        elif task == 'update':
            log.info('Updating requirements ...')
            
        subprocess.call('pip install -r Requirements.front.txt', shell=True)
        
        if task == 'generate':
            log.info(f'Requirements.front.txt file generated on current {env} environment')
            log.info(f'Project requirements handled successfully for {env} environment')
            
        elif task == 'update':
            log.info(f'Requirements.front.txt file updated on current {env} environment')
            log.info(f'Project requirements handled successfully for {env} environment')
            
    elif task == 'install':
        
        try:
            # try to install dependencies from the requirements.front.txt file
            log.info('Installing requirements ...')
            
            subprocess.call('pip install -r Requirements.front.txt', shell=True)
            
            log.info(f'Requirements.front.txt file installed successfully on current {env} environment')
            log.info(f'Project requirements handled successfully for {env} environment')
        except Exception as exception:
            log.error(f'Error while installing dependencies for {env} environment')
            log.error(exception) 
            log.error("If there is an error at this stage, it means that the python environment has some incompatibilities with the requirements.front.txt packages")
            log.error("Try rebuilding the clean python docker image and install the dependencies for this project again")
            log.error(f'Project requirements not handled correctly for {env} environment')
            
    else:
        log.error('Invalid task for requirements inserted')
        raise Exception('Invalid task, please use generate, update or install')
        log.error('Requirements.front.txt file not generated')
    

def requirements_main(env = None):
    """
    The function takes in an environment variable as an argument, if the environment variable is not
    specified on call, the function will look for the environment variable in the os.environ.get('ENV')
    function.
    
    If the environment variable is set to development or dev, the function will generate a
    requirements.front.txt file, if the file already exists, the function will update the file. 
    
    If the environment variable is set to production or prod, the function will install the dependencies
    from the requirements.front.txt file. 
    
    If the environment variable is set to None, '', ' ', 'null' or 0, the function will raise an
    exception. 
    
    :param env: The environment you want to install the dependencies for
    """
    
    current_env = os.environ.get('ENV') if env is None else env
    try:
        # look through the possible ENV variable values for development or production, if none of these, raise an exception
        if current_env in ['development','dev']:
            
            if os.path.exists('Requirements.front.txt'):
                # remove previous requirements.front.txt file 
                os.remove('Requirements.front.txt')
                requirements('update', current_env)
                
            else:
                # create a new requirements.front.txt file
                requirements('generate', current_env)
                
        elif current_env in  ['production','prod']:
            #install dependencies from the requirements.front.txt file
            requirements('install', current_env)
            
        elif current_env in [None, '', ' ', 'null', 0]:
            str(current_env)
            log.error(f'Invalid environment inserted or no environment specified, current environment is set to "{current_env}"')
            raise InvalidEnvorimentError('Invalid environment, please use development, dev or production, prod')
    
    except InvalidEnvorimentError as exception:
        log.error(exception) 
        log.error('Please insert a valid environment variable in order to proceed with the program')
        log.error('Requirements.front.txt could not be handled')
        log.error('Project initialization failed')
        
    log.info('Project initialization successful') 
    
        
if __name__ == '__main__':
    requirements_main()