# Nova Planning

Planning for Computer Science classes at UMONS 

This repository is split in two parts :
- The scraper that gets the schedule of each class 
- The web app that lets you see your planning 

The planning is accessible with this link : https://tonitch.github.io/NovaPlanning/

## Scraper
It's made in python using selenium, it's like a bot opening a browser and
moving the cursor to a specific location to get on the pages where it can find
the classes timetable. Then I scrap the data that I need out of thoses pages.
The information is stored inside __event.json__ file.

The scraper is executed every day using Github Action.

## Web App
Web App is made using simple html/css/js, it uses fullcalendar to make a good
calender viewer. When too much classes are at the same time of the day, the
text can be sometimes out of the box. For this problem, tooltip was used to
make a "bubble" with the text the mouse is over the class schedule.

## Credits
This is a fork from https://github.com/MokonaNico/NovaPlanning
Thanks to him to let me improve it my own way
