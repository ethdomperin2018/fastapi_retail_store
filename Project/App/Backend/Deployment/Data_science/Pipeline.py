from feature_engineering import feature_engineering_main
from model_building import model_building_main
from model_evaluation import model_evaluation_main
from model_prediction import model_prediction_main
from model_report import model_report_main

def data_science_pipeline_mainenv_config():
    current_env, deploy_method = get_envs(env_config)
    
    feature_engineering_main()
    model_building_main()
    model_evaluation_main()
    model_prediction_main()
    model_report_main()
    return True