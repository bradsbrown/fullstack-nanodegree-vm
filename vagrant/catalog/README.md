# Household Inventory Database
This system has been created as a way to track, view, and keep a list of all the important items in your house. It can be a great way to prepare a report should anything ever go missing due to theft of acts of nature. Let's walk through how to get this rolling, so you can start protecting your valuables!

# Setup
If you are at all familiar with Python, this should be a quick and easy process.
1. In your terminal (CLI), navigate into the 'catalog' directory.
1. Set up your database by running `python database_setup.py` in the CLI.
1. edit `fb_client_secrets.json` to fill in your own `app_id` and `app_secret` from the Facebook developer page.
1. Now, you can start your server by running `python project.py`
1. Now, in your browser, the site can be found at `http://localhost:5000`.
1. You're ready to go!

# Usage
A few things to note:
* All user logins are via Facebook authorization, for a secure and reliable login process.
* Anyone can _browse_ the inventory without restriction.
* Only logged in users can _add or edit_ rooms.
* Any items added are marked as being owned by the logged in user creating them.
* Only the user who created an item in the database can edit or delete that item.

# Data Export
This site contains a few JSON outlets to get data out for use in other systems. They are:
* `/rooms/JSON` - exports a list of room names and IDs
* `/items/JSON` - a full list of all items with all properties
* `/item/(item id)/JSON` - a list of all properties for a single item
* `/rooms/(room id)/JSON` - a list of all properties for items in a single room
* `/owners/JSON` - a directory of all users in the database


Let me know if you have any questions/issues!
