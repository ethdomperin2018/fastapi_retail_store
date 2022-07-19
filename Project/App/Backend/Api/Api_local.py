import os
import pickle
import pandas as pd
import requests
import json
from flask import Flask, request, Response, render_template, abort
#from folder.file import class
from Store_Sales_Analysis import Store_Sales_Analysis

def send_message(chat_id, text):
    url = 'https://api.telegram.org/bot{}/'.format(TOKEN)
    url = url + 'sendMessage?chat_id={}'.format(chat_id)
    
    api_call = requests.post(url, json = {'text': text })
    print('Status Code {}'.format(api_call.status_code))
    
    return None

#middleware
def get_prediction(data):
    # API Call
    # makes an API call to /predict endpoint
    url_prod = 'https://andrew-store-sales-analysis.herokuapp.com/predict'
    dev_url = 'http://127.0.0.1:8000/predict'
    url = dev_url
    header = {'Content-type': 'application/json'}
    #data = data
    
    api_call = requests.post(url, data = data, headers = header)
    
    print(f'Status Code {api_call.status_code}')
    
    prediction = pd.DataFrame(api_call.json(), columns = api_call.json()[0].keys())
    
    return prediction

def load_model(model_name):
    # loading model in readbytes mode
    current_path = os.path.dirname(os.path.abspath(__file__))
    model = pickle.load(open(current_path + model_name + '.pkl', 'rb'))
    
    return model

def load_dataset(store_id):
    # loading test dataset
    try:
        df_test_raw = pd.read_csv('test.csv')
        df_store_raw = pd.read_csv('store.csv')
        #print('\n **#** datasets loaded successfully **#** \n')
    except Exception as e:
        print('error loading datasets')
        print(e)
    # merge test dataset + store
    df_test = pd.merge(df_test_raw, df_store_raw, how = 'left', on = 'Store')
    
    # choose store for prediction
    df_test = df_test[df_test['Store'] == store_id]
    
    if not df_test.empty:
        # remove closed days
        df_test = df_test[df_test['Open'] != 0]
        df_test = df_test[~df_test['Open'].isnull()]
        df_test = df_test.drop('Id', axis = 1)
        # convert Dataframe to json
        data = json.dumps(df_test.to_dict(orient = 'records'))
        # check now many rows are in the dataframe using .shape (rows, columns)
        #print(f'\n **#** {df_test.shape[0]} rows in the dataset **#** \n')
        #print(f'\n **#** {df_test.shape[1]} columns in the dataset **#** \n') 
        #print(f'\n **#** {len(df_test)} rows in the dataset **#** \n')
    else:
        data = 'error'
        
    return data

def parse_message(message = None):
    #print(type(message))
    chat_id = message['message']['chat']['id']
    store_id = message['message']['text']
    store_id = store_id.replace('/', '')
    
    try:
        store_id = int(store_id)
        
    except ValueError:
        print('Store id needs to be a number')
        store_id = 'error'
        
    return chat_id, store_id

def get_response(response, error = None, endpoint = None,  message_chat_id = None, message_text = None):
    
    #implement with match case with python 3.10
    if response == 0: #debug one
        message =  {'Keys': 'are ok',
                    'message_chat_id': message_chat_id,
                    'message_text': message_text,
                    'endpoint': endpoint}
    elif response == 1:
        message =  {"hello": r"Greetings, I am a telegram bot",
                    "error": r"There are missing keys in the request",
                    "instruction": r"Please send a json object with the following keys:",
                    "message": r"{ chat: {id:chat_id, type:chat_type}, text:/some_text}",
                    "goodbye": f"This proofs you could access the endpoint {endpoint}"}
    elif response == 2:
        message = {"error": "No data received, json empty, please send a valid json object"}
    elif response == 3:
        message = {"error": "No json received, data header doesn't indicate a json object, please send a json object"}
    elif response == 4:
        message = {"error": "Method not allowed"}
    elif response == 5:
        message = {"success": "Message sent to telegram chat successfully with prediction"}
    elif response == 6:
        message =  {"success": "Message sent to telegram chat successfully but no prediction was made",
                    "error": error}
        
    message = json.dumps(message)
    
    return message

def check_json(data = None, endpoint = None, method = None):
    
    # check if request.content_type is json or if it is empty
    if (data.content_type != '' and data.is_json): #check if data header indicates json and is not empty
        # remove empty check in case telegram doesn't send correct headers with json type
        # perhaps remove it entirely if telegram doesn't send headers at all
        received_json = data.get_json()
        # log json received
        if any(received_json):
            # check if required keys are in the json
            # can add more later if needed
            try:
                message_chat_id = received_json['message']['chat']['id']
                message_text = received_json['message']['text']
                # log json not empty, keys are in the json
                # comment when debugging
                
            except Exception as e:
                # only error that can occur here is if some key doesn't exist
                # log json not empty, error key not found
                # return instructions
                abort(Response(get_response(1, None, endpoint), status = 400, mimetype = 'application/json'))
                
            finally:
                
                if method == 'GET':
                    # return instructions
                    abort(Response(get_response(1, None, endpoint), status = 400, mimetype = 'application/json'))
                    
                else:
                    # return json
                    return received_json
                # comment when deploying
                # return abort(Response(get_response(0, None, endpoint, message_chat_id, message_text), status = 200, mimetype = 'application/json'))
        else:
            # return error, json is empty
            abort(Response(get_response(2), status = 400, mimetype = 'application/json'))
    else:
        # return error, data header doesn't indicate a json object
        abort(Response(get_response(3), status = 400, mimetype = 'application/json'))

def check_entrypoint(call = None, endpoint = None):
    
    if endpoint in ['/telegram', '/webapp']:
        # external endpoint, need to check if method is GET or POST or other
        if call.method == 'POST':
            #log post method requested
            call_json = check_json(request, endpoint, 'POST')
            
            return call_json
            
        elif call.method == 'GET':
            #log get method requested
            check_json(request, endpoint, 'GET')
            
        else:
            # log other method requested
            # return method not allowed
            abort(Response(get_response(4), status = 400, mimetype = 'application/json'))
            
    elif endpoint == '/predict':
        # internal endpoint, no need to check method
        call_json = call.get_json()
        
        return call_json
    
# API initialization
app = Flask(__name__, static_folder='Static')

@app.route('/home')
def index():
    
    return render_template('index.html')

@app.route('/webapp')
def webapp():
    
    return '<p> Welcome to the webapp </p>'
    # return render_template('webapp.html')

@app.route('/telegram', methods = ['GET', 'POST'])
def telegram_bot():
    
    received_json = check_entrypoint(request, endpoint = '/telegram')
    
    chat_id, store_id = parse_message(received_json)
    
    if store_id != 'error':
        # loading data
        data = load_dataset(store_id)
        
        # if not returned an empty dataset (string 'error') because store_id doesn't exist
        if data != 'error':
            # prediction call
            prediction_df = get_prediction(data)
            # calculation
            pred_group_df = prediction_df[['store', 'prediction']].groupby('store').sum().reset_index()
            # get store number
            store = pred_group_df['store'].values[0]
            # get prediction value
            prediction = pred_group_df['prediction'].values[0]
            # convert to number
            prediction = float(prediction)
            # send message with store number and prediction in text format to telegram bot chat
            msg = f'Store Number {store} will sell R${prediction:,.3f} in the next 8 weeks'
            print(msg)
            #send_message(chat_id, msg)
            # return message sent to telegram chat, in this case, success
            return Response(get_response(5), status=200)
        
        else:
            error = 'Store Not Available'
            send_message(chat_id, error)
            # return message sent to telegram chat, in this case, error
            return Response(get_response(6, error = error), status=200)
        
    else:
        error = 'Store ID must be a number'
        send_message(chat_id, error)
        # return message sent to telegram chat, in this case, error
        return Response(get_response(6, error = error), status=200)

@app.route('/predict', methods = ['GET', 'POST'])
def model_predict():
    
    received_json = check_entrypoint(request, endpoint = '/predict')
    
    model = load_model('/Models/XGBoost_Regressor_Tuned')
    
    # redo this later, strange check (?). Must be a better way to do this
    if isinstance(received_json, dict): # unique example
        X_test = pd.DataFrame(received_json, index = [0])
    else: # multiple example
        X_test = pd.DataFrame(received_json, columns = received_json[0].keys())
    
    pipeline = Store_Sales_Analysis()
    
    data_cleaned = pipeline.data_cleaning(X_test)
    
    feature_extracted = pipeline.feature_extraction(data_cleaned)
    
    data_prepared = pipeline.data_preparation(feature_extracted)
    
    prediction = pipeline.get_prediction(model, X_test, data_prepared)
    
    #return prediction
    return Response(prediction, status=200, mimetype = 'application/json')

if __name__ == '__main__':
    port = os.environ.get('PORT', 8000)
    host_prod = os.environ.get('HOST', '0.0.0.0')
    host_dev = os.environ.get('HOST', '127.0.0.1') 
    app.run(host = host_dev, port = port)
    #app.run()