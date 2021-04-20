# Data Cleaning Tool
### Dependencies
The backend of the tool is written in Python3 and depends on the following libraries:
Name | URL | Install
:--- | :--- | :---
scikit-learn | https://scikit-learn.org/stable/index.html | ```pip install scikit-learn```
Flask | https://flask.palletsprojects.com/en/1.1.x/ | ```pip install Flask```
Jinja2 | https://jinja.palletsprojects.com/en/2.11.x/ | ```pip install Jinja2```
Pandas | https://pandas.pydata.org/ | ```pip install pandas```
Unidecode | https://pypi.org/project/Unidecode/ | ```pip install Unidecode```

Make sure you have Python3 and pip installed with the dependencies in the table above.
### Usage
1. Go to data_cleaning/tables.txt and insert the absolute paths of the .csv-files that you want to clean. **Do not move, rename or delete this file!**
2. Go to the root folder of this project and execute ```python -m data_cleaning.start_server```. This will start the server and process the data.
    - To run the program on a specific port, run ```python -m data_cleaning.start_server -p PORTNUMBER```, with *PORTNUMBER* any portnumber you want. By default, the program will run on port 5000.
    - Functional dependencies are disabled by default since version v1.1.0. Add  ```--enable-functional-dependencies``` to the command to enable this functionality.
3. Go to http://127.0.0.1:5000/ (or to another port) to use the client and start your cleaning procedure.
