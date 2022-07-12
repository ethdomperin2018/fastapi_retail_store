# Backend App --> Dockerfile
# This is the Dockerfile for the backend app using Python and Poetry as package manager
# This is meant to be a minimal setup
FROM python:3.9-slim
# Comes from docker-compose file, which gets it from Dev.env or Prod.env file 
ARG APP_ENV
# These variables will persist on the final image
ENV App_env=${APP_ENV}\
    PYTHONDONTWRITEBYTECODE=1\
    PYTHONFAULTHANDLER=1\
    PYTHONUNBUFFERED=1\
    PYTHONHASHSEED=random\
    PIP_NO_CACHE_DIR=off\
    PIP_DISABLE_PIP_VERSION_CHECK=1\
    PIP_DEFAULT_TIMEOUT=100\
    Virtual_env=/App/Backend/venv/\
    Poetry_version=1.1.13\
    Poetry_init_config="poetry config virtualenvs.create false"\
    Poetry_install="poetry install --no-interaction --no-ansi --no-root"\
    Poetry_prod="--no-dev"
# Copies the Backend app files to the container
COPY . /App/Backend

# Defines the current working directory to the Backend app's Build folder
WORKDIR /App/Backend/Build
# Installs Poetry as a package manager in the given version on system's Python
RUN pip install "poetry==${Poetry_version}"
# Create a virtualenv, Poetry remains on system's Python while the Backend app runs alone in a virtualenv
RUN python3 -m venv ${Virtual_env}
# Activating the virtualenv to every command after this
ENV PATH="${Virtual_env}/bin:${PATH}"

# Checks if the current environment is development or production
# Installs the dependencies according to the environment
RUN if [ "${App_env}" = "development" ] || [ "${App_env}" = "dev" ] ; then\
    ${Poetry_init_config} && ${Poetry_install};\
    elif [ "${App_env}" = "production" ] || [ "${App_env}" = "prod" ] ; then\
    ${Poetry_init_config} && ${Poetry_install} ${Poetry_prod};\
    fi
# Opens the port for the Backend app, works only for docker deployments
EXPOSE 8000

# Defines the current working directory to the Backend app's main folder
WORKDIR /App/Backend
# ENTRYPOINT ["./App/Backend/Build/docker-entrypoint.sh"]
# An entrypoint script can be defined to run a command before the app starts:
# make migrations first time
# In case of using Heroku, the port is random, so it should be used like --port=${PORT} to detect Heroku's port
CMD ["uvicorn", "Backend:app", "--host=0.0.0.0", "--port=8000", "--reload"]