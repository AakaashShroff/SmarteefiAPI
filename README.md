# SmarteefiAPI
This script utilises the smarteefi website to control appliances from a script overcoming the need to have multiple boards to be eligible to request an API access

This script allows you to control smarteefi appliances through selenium and a local script which can be made into an API with flask.

It uses selenium to control appliances based on user input, you can run it --headless.

This script is made for my requirement so it selects another home I named 'Nikoo' for appliance control, you can modify the script to either directly control appliance(remove the select nikoo function) or select another home(change name in select nikoo function based on your need).

Make changes in the script: change the switch name and its respective toggle id(inspect page to see it). in my case 'Switch-1' had a input tag for the toggle whose name was 'ion-tg-5'. This switch was for my light and i refer to it as light in my script. Change according to your need.

Add your smarteefi credentials in the .env file and run the script
