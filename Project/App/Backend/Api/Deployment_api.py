# Use Fastapi!!!!

def deploy_main():
    print("Running FastAPI deployment pipeline")
    
# GET request from Frontend
# with the response from the trained model
# make a POST request to the database to register
# both the data from the GET request from the Frontend and the prediction response from the trained model
# this POST request will be sent to the database to 
# register the request and the prediction made at the time on the table
# The model is located on the production folder inside the models folder
# The scalers are located on the scalers folder inside the models folder

if __name__ == "__main__":
    deploy_main()