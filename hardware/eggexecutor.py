import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

availableEggs = filter(lambda egg: egg.startswith('run_'), os.listdir("."))
eggs = {}
for egg in availableEggs:
    line = open(egg).readline()
    if 'unuse' not in line:
        lines = line[1:].split(':')
        eggs[lines[0].lower()] = {
            "title": lines[1],
            "file": egg
        }
    
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""  
  |  {bcolors.BOLD}Hallo! Ich bin die Ostereimaschine.{bcolors.ENDC}
  |  Ich kann verschiedenste Muster zeichnen, wie etwa Blumen oder Musiknoten, die unten aufgelistet sind.
  |  Du musst mir nur sagen was ich machen soll, indem du den Namen deines Lieblingsmusters in die Zeile
  |  schreibst und dann <ENTER> drückst.
  |  Wenn du mich jedoch beenden willst, drücke einfach <Ctrl+C>.
  |  Ich freue mich schon auf meine nächste Aufgabe! :-)
  ___________________________________________________
""")
    for key, value in eggs.items():
        print(f'{bcolors.BOLD}Muster "{key}":{bcolors.ENDC}\n{value["title"]}')
       
    file = None
    while file == None:
        name = input(f'{bcolors.OKBLUE}Gib hier bitte dein Muster ein:{bcolors.ENDC}{bcolors.BOLD} ').lower()
        file = f'/home/pi/Robotik/Ostereimaschine2.0/hardware/{eggs[name]["file"]}' if name in eggs else None
        if file == None:
            print(f'{bcolors.ENDC}{bcolors.WARNING}Das habe ich leider nicht verstanden. Könntest du das bitte nochmal wiederholen?{bcolors.ENDC}\n')
            
    argument = input(f'{bcolors.ENDC}{bcolors.OKBLUE}Willst du dir das Ei erstmal nur angucken (<S> drücken) oder gleich drucken (<C> drücken)?{bcolors.ENDC}{bcolors.BOLD} ').lower()
    argument = 'C' if argument == 'C' else 'S'    
    os.system(f'python3 {file} {argument} > /dev/null &')