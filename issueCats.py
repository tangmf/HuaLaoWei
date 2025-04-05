
# Online Python - IDE, Editor, Compiler, Interpreter

l = '''Illegal Parking
> Road
> HDB/URA Car Park
> Motorcycle at Void Deck

Facilities in HDB Estates
> Lightning Maintenance
> Common Area Maintenance
> HDB Car Park Maintenance
> Playground & Fitness Facilities Maintenance
> Bulky Waste in Common Areas

Roads & Footprints
> Damaged Road Signs
> Faulty Streetlight
> Covered Linkway Maintenance
> Road Maintenance
> Footpath Maintenance

Cleanliness
> Dirty Public Areas
> Overflowing Litter Bin
> High-rise Littering
> Bulky Waste in HDB Common Areas

Pests
> Cockroaches in Food Establishment
> Mosquitoes
> Rodents in Common Areas
> Rodents in Food Establishment
> Bees & Hornets

Animals & Bird
> Dead Animal
> Injured Animal
> Bird Issues
> Cat Issues
> Dog Issues
> Other Animal Issues

Smoking
> Food Premises
> Parks & Park Connectors
> Other Public Areas

Parks & Greenery
> Fallen Tree/Branch
> Overgrown Grass
> Park Lighting Maintenance
> Park Facilities Maintenance
> Other Parks and Greenery Issues

Drains & Sewers
> Choked Drain/Stagnant Water
> Damaged Drain
> Flooding
> Sewer Choke/Overflow
> Sewage Smell

Drinking Water
> No Water
> Water Leak
> Water Pressure
> Water Quality

Construction Sites
> Construction Noise

Abandoned Trolleys
> Cold Storage
> Giant
> Mustafa
> FairPrice
> ShengSong
> Ikea

Shared Bicycles
> Anywheel
> HelloRide
> Others

Others
> Others'''.split("\n")

currCatName = ""
catList = {}
for item in l:
    if item == "":
        continue

    # if new cat
    if item[0:2] != "> ":
        currCatName = item
        catList[currCatName] = []
    else:
        catList[currCatName].append({"label": item[2:], "value": item[2:]})

print(catList)

