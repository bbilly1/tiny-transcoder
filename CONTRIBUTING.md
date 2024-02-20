# Contributing to Tiny Transcoder

## Dev Environment
Example how to set up your development environment.

1. Clone this repo
2. Create your virtual environment and install the dev requirements, e.g. from the project root:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```
3. Change to the `app` directory, and install the node dependencies, e.g.:
```bash
cd app
npm install
```
4. From the same `app` directory run application in debug mode to automatically reload on change:
```bash
TT_APP="." TT_CACHE="/media/DATA/temp/cache" flask run --debug --port 8000
```
5. Open a separate terminal window, from the `app` directory run webpack in watch mode to automatically rebuild on change:
```bash
npx webpack --config webpack.config.js --mode development --watch
```
6. Open [localhost:8000](http://localhost:8000) in your browser of choice to access the application.
