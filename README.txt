======== eBird Lifer Alert ========
			Caleb Frome

eBird Lifer Alert is a personal project I developed to generate a customizable list of nearby birds that I haven't seen, based on eBird reports. The goal is to build upon the existing eBird alerts feature, adding customization options to make a more useful tool, though perhaps sacrificing some simplicity and ease of use.

To get started using this program, you'll need Python 3 installed on your computer, plus a few other libraries (listed in the import statements at the beginning of createAlert.py). This process can be streamlined using an IDE such as PyCharm - this is particularly useful if you plan to make any changes to the code. The venv directory should be located in the top-level eBirdLiferAlert directory that contains all of the other files. I didn't include my venv directory in this repository because of its size and dynamic nature, but if you have trouble setting up the environment, I can provide it.
Once that's working, you'll want to edit config.json to personalize the program. You'll have to provide your eBird username and password (don't worry, no one can access any of your local files) and the list of states you want alerts from. There are a few other settings here as well, including:

combine
- none:		don't combine any alerts (default)
- county:	combine alerts of the same species within the same county (and state)
- state:	combine alerts of the same species within the same state
- all:		combine all alerts of the same species

aba_rare
- 3/4/5:	include reports of birds anywhere in the ABA area whose ABA rarity code is at least this number
- off:		don't include reports of any rare birds outside the chosen regions

output
- none:		don't display any results (the output.html file is still created)
- browser:	open the about.html results file in a browser
- desktop:	display the results as desktop notifications
	
After the environment has been set up, any Python IDE can easily run the program, or you can run createAlert.bat.

The entire project open-source and publicly available. If you're interested in my future plans for the project, check out the Projects tab. If you need any help getting started, have any additional suggestions, find a bug, or you're interested in collaborating, let me know!
