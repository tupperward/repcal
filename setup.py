from os.path import exists 
import genRSS
from dateObject import carpeDiem, addDayToTop10, upkeepTop10

if not exists('./static/atom.xml'):
    today = carpeDiem()
    upkeepTop10()
    addDayToTop10(today)
    genRSS.main()
