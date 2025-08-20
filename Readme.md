## Install

#### Create Environment with venv or conda:
Venv:
```
python3 -m venv .venv
source .venv/bin/activate
```
    
Conda:
```
conda create --name raas python=3.9
conda activate raas
```

#### Install packages:
```
pip install -r requirements.txt
``` 

#### Download required spaCy models
```
python -m spacy download en_core_web_lg
python -m spacy download de_core_news_lg
```

