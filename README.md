# Halite4Starter
This is just a simple greedy starter bot for Halite season 4. Last year, the Two Sigma team gave us a lot of great bots to get started with so more time could be spent on working on your bot, and less on simply parsing game data. Unfortunately, they did not do that this year. I decided to convert some of the basic features from my previous year's Java bot into Python. Kaggle only allows for a single file upload, so that's why I have put all the code in `submission.py`.

## To run the bot:
It's recommended to create a virtualenv:
```commandline
cd Halite4Starter/
virtualenv venv
source venv/bin/activate 
```

Install the requirements:
```commandline
pip install -r requirements.txt
```

Run the bot:
```commandline
python run.py
```

That's it! There's a notebook version as well (`run.ipynb`) if you prefer that over the commandline. The commandline version will save the output as an html file which can be viewed in your browser. The notebook version will render it in IPython.
