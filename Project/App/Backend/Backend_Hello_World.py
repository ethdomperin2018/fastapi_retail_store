from fastapi import FastAPI
import os
import subprocess
app = FastAPI()

@app.get("/")
def root():
    try:
        # assure we are running inside virtualenv and not in system python
        env = str(subprocess.check_output(["pip", "-V"]))
    except:
        env = "Failed"
    if "/Backend/venv/" in env:
        env = "Running inside virtualenv"
        
    return {"message": "hello world",
            "here": "From Backend.py",
            "env": env}