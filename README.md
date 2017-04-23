# HTTPS Everywhere Safari Test
A few hour's effort to see if HTTPS Everywhere could be ported to Safari. Inspired by https://github.com/EFForg/https-everywhere/issues/5121

## Summary
* Yes, you can have something similar to HTTPS Everywhere functionality in Safari
* There are problems with this functionality though (detailed in Notes section)
* There may be ways around this problem that haven't been explored yet
* You can download this repo and follow the Installation/Running instructions to see for yourself

## Installation/Running
1. Open up Safari and if you haven't already actived the developer menu, go to Preferences(⌘,) -> Advanced and check the box that says "Show Develop menu in menu bar"
2. Go to the Develop menu and select "Show Extension Builder"
3. Click Continue when the dialog pops up
4. In the bottom left-hand corner there is a plus sign, click it and click "Add Extension..."
5. Select the "Test-HTTPS-Everywhere.safariextension" folder that is included in this repo
6. To run, click the install button in the top right-hand corner. It will ask you to confirm and for your password
7. It should work now. See Notes for what to expect when it's running and Editing Rules for how to edit the rules

## Editing Rules
* To edit the rewrite rules, simply edit the sites.json file located in the safariextension folder
* You can also create another JSON file in the same folder and get the extension to use it by selecting it under the "Content Blocker" option in the Extension Builder window
* **Every time you edit the JSON file, you need to reload the extension (top right-hand corner)**

## Notes
* While the script can generate a JSON file with ~75% of HTTPS Everywhere's rewrite rules (~700,000 lines of JSON), Safari seems to only be able to handle small JSON files
  * I got a "JSON Compilation failed" error for every JSON file generated with >=750 HTTPS Everywhere rulesets
  * 500 rulesets (~13,000 lines) in one file worked so the maximum is somewhere between 500 and 750 rulesets
  * I don't know if you could compile it and distribute a binary that had more than 500 rulesets
* The rewriting definitely works, it just only seems to work in certain situations
  * It seems to work if there's a redirect
    * Ex: http://msn.com redirects to http://www.msn.com which seems to trigger an https rewrite
    * If you go directly to http://www.msn.com, it doesn't seem to triggger an https rewrite
  * It seems to work if you refresh the page
  * Once a site has been rewritten once, it seems to rewrite links more readily in the future
    * Ex: After loading msn.com over https, it seems to rewrite future http://www.msn.com to https
    * I don't know how long this effect lasts
* I just built the Extension using Safari's Extension Builder but Apple also offers the option of building extensions with XCode
  * I don't know if that could get around some of the limitations I've found here
  * A link to Apple's docs about that is in the Useful Links section
* I included 5 sites that I know normally default to http but can be successfully rewritten to https at the top of the sites.json file
  * After those I put the JSON output from running my script on the HTTPS Everywhere rulesets with `--limit 500`

## Useful Links
* [Creating content blocking (https rewrite) rules](https://developer.apple.com/library/content/documentation/Extensions/Conceptual/ContentBlockingRules/CreatingRules/CreatingRules.html)
* [Example content blocker that was helpful for learning what to do](https://github.com/krishkumar/BlockParty/tree/master/BlockParty%20-%20Desktop%20Safari)
* [Tutorial about building a Content Blocker in iOS (the principles are mostly the same for iOS and macOS)](https://www.hackingwithswift.com/safari-content-blocking-ios9)
* [Docs about creating extensions in XCode](https://developer.apple.com/library/content/documentation/NetworkingInternetWeb/Conceptual/SafariAppExtension_PG/index.html)

## Python Script
* I wrote the python script to help me generate the JSON for the Safari Extension
* The script has command-line options for specifying
  * A specific XML file to use
  * The directory (of XML files) to use
  * Where to output the JSON
  * The maximum number of XML files to parse
* The options can be displayed by running `python3 gen_json.py -h`
* You can change the JSON the script outputs by changing the object in the generate_json() function
  * Line 108 of the script currently
* The script avoids trying to parse rulesets with exclusions or more than one rewrite rule
* I wrote the script rather quickly so there might be errors in it

## Python Script Dependencies
* Python 3
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  * Can be installed with [pip](https://pypi.python.org/pypi/pip/) by running `pip install beautifulsoup4`
* [lxml](http://lxml.de/index.html)
  * Can be installed with pip by running `pip install lxml`
