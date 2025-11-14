#This file gives the console commands to link the repo to the hugging face space

git remote add hf_REnergy https://huggingface.co/spaces/REnergies99/API_REnergy

git pull -s subtree

git subtree split --prefix=code/0X_API -b hf-subtree
git push hf_REnergy hf-subtree:main --force
git branch -D hf-subtree



git subtree push --prefix=code/0X_API hf_REnergy main