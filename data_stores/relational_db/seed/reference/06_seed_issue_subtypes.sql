INSERT INTO issue_subtypes (issue_type_id, name, description) VALUES
(1, 'Road', 'Illegal parking of vehicles on public roads, bus lanes, or yellow-zoned areas.'),
(1, 'HDB or URA car park', 'Illegal parking within HDB or Urban Redevelopment Authority-managed car parks.'),
(1, 'Motorcycle at void deck', 'Motorcycles parked illegally under residential void decks.'),

(2, 'Lighting maintenance', 'Maintenance issues related to malfunctioning corridor lights, streetlamps, or common area lighting.'),
(2, 'Common area maintenance', 'Damage, defects, or safety issues in common areas such as lift lobbies, stairwells, or corridors.'),
(2, 'HDB car park maintenance', 'Problems related to HDB car park surfaces, markings, or structures.'),
(2, 'Playgrounds or fitness facilities maintenance', 'Damaged or unsafe playground equipment or fitness stations in HDB estates.'),
(2, 'Bulky waste in common areas', 'Uncollected bulky waste items like furniture left in void decks or corridors.'),

(3, 'Dirty public areas', 'General uncleanliness observed in public spaces like parks, streets, or common corridors.'),
(3, 'Overflowing litter bins', 'Public bins that are overflowing with trash and require urgent emptying.'),
(3, 'High-rise littering', 'Littering activities from upper floors of residential or commercial buildings.'),
(3, 'Bulky waste in HDB common areas', 'Large discarded items improperly left at HDB common areas, causing obstruction.'),

(4, 'Damaged road signs', 'Broken, missing, or obscured traffic and road signage.'),
(4, 'Faulty streetlights', 'Non-functioning or flickering streetlights along roads or walkways.'),
(4, 'Covered linkway maintenance', 'Maintenance issues such as cracks, leaks, or damages in covered pedestrian walkways.'),
(4, 'Road maintenance', 'Potholes, road cracks, or other defects in vehicle roads.'),
(4, 'Footpath maintenance', 'Cracks, uneven surfaces, or damage on pedestrian walkways.'),

(5, 'Dead animals', 'Carcasses of animals found in public spaces requiring removal.'),
(5, 'Injured animals', 'Wounded or distressed animals in public areas needing rescue.'),
(5, 'Bird issues', 'Problems caused by bird droppings, nesting, or aggressive bird behaviour.'),
(5, 'Cat issues', 'Issues involving stray or nuisance cats, including welfare or disturbances.'),
(5, 'Dog issues', 'Issues involving stray, lost, or nuisance dogs in public areas.'),
(5, 'Other animal issues', 'Animal-related reports not falling under cats, dogs, or birds.'),

(6, 'Cockroaches in food establishments', 'Sightings or infestations of cockroaches in eateries or food shops.'),
(6, 'Mosquitoes', 'Reports of mosquito breeding sites or high mosquito populations.'),
(6, 'Rodents in common areas', 'Rat or mouse sightings in shared residential or public spaces.'),
(6, 'Rodents in food establishments', 'Presence of rodents in food-related businesses or hawker centres.'),
(6, 'Bees and hornets', 'Presence of bee or hornet nests posing potential safety threats.'),

(7, 'Fallen trees or tree branches', 'Obstructions caused by fallen trees or branches on public roads, parks, or walkways.'),
(7, 'Overgrown grass', 'Public grassy areas that are excessively tall or poorly maintained.'),
(7, 'Park lighting maintenance', 'Faulty lighting systems inside parks or along park connectors.'),
(7, 'Park facilities maintenance', 'Broken or vandalised park structures such as benches, shelters, or exercise equipment.'),
(7, 'Other parks and greenery issues', 'Other maintenance issues affecting parks, gardens, or green connectors.'),

(8, 'Food premises', 'Smoking observed inside or directly outside food establishments.'),
(8, 'Parks and park connectors', 'Smoking incidents within parks or park connector networks.'),
(8, 'Other public areas', 'Smoking observed at places like bus stops, markets, and public walkways.'),

(9, 'anywheel', 'Issues related to abandoned or improperly parked Anywheel shared bicycles.'),
(9, 'HelloRide', 'Issues related to abandoned or improperly parked HelloRide shared bicycles.'),
(9, 'Other bicycle sharing providers', 'Shared bicycle issues related to other operators not specifically listed.'),

(10, 'Cold Storage', 'Abandoned supermarket trolleys originating from Cold Storage stores.'),
(10, 'Giant', 'Abandoned supermarket trolleys originating from Giant supermarkets.'),
(10, 'Mustafa', 'Abandoned shopping carts from Mustafa Centre.'),
(10, 'FairPrice', 'Abandoned supermarket trolleys from FairPrice outlets.'),
(10, 'ShengSong', 'Abandoned supermarket trolleys from Sheng Siong supermarkets.'),
(10, 'Ikea', 'Abandoned shopping carts from IKEA outlets.'),

(11, 'Choked drains or stagnant water', 'Blockages in drainage systems causing stagnant water build-up.'),
(11, 'Damaged drains', 'Physical damage to drainage systems such as cracks or collapsed segments.'),
(11, 'Flooding', 'Accumulation of water on roads or pathways after rain due to poor drainage.'),
(11, 'Sewer choke or overflow', 'Sewage system blockages causing backflows or overflows.'),
(11, 'Sewage smell', 'Foul odours emanating from sewer lines or manholes.'),

(12, 'Construction noise', 'Excessive noise caused by ongoing building or infrastructure construction activities.'),

(13, 'No water', 'Complete disruption of potable water supply at a property.'),
(13, 'Water leakages', 'Water loss due to leaking pipes, taps, or fittings.'),
(13, 'Water pressure', 'Significant drop or fluctuations in water pressure at premises.'),
(13, 'Water quality', 'Issues with the taste, colour, or safety of supplied water.'),

(14, 'Miscellaneous', 'Other municipal issues that do not match predefined categories.')
ON CONFLICT (name) DO NOTHING;
