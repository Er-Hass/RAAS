import subprocess

# Install required Python packages
subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)

# Download SpaCy models
subprocess.run(['python', '-m', 'spacy', 'download', 'en_core_web_lg'], check=True)
subprocess.run(['python', '-m', 'spacy', 'download', 'de_core_news_lg'], check=True)
