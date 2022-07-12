from data_collection import data_collection_main
from data_cleaning import data_cleaning_main
from exploratory_analysis import exploratory_analysis_main

def data_analysis_pipeline_main():
    
    data_collection_main()
    data_cleaning_main()
    
    if current_env in ['development', 'dev']:
        exploratory_analysis_main()
    
    return True
