INSERT INTO issue_types (issue_type_id, name, description) VALUES
(1, 'Illegal Parking', 'Reports of vehicles parked illegally along roads, car parks, or HDB estates.'),
(2, 'Facilities in HDB Estates', 'Maintenance issues related to facilities in Housing Development Board (HDB) residential estates.'),
(3, 'Cleanliness', 'Concerns regarding public hygiene, such as littering, dirty areas, or improper waste disposal.'),
(4, 'Roads and Footpaths', 'Defects or maintenance issues concerning public roads, streets, footpaths, or covered linkways.'),
(5, 'Animals & Birds', 'Issues involving stray, injured, dead animals or bird-related disturbances in public spaces.'),
(6, 'Pests', 'Reports of pest sightings including cockroaches, mosquitoes, rodents, or bee infestations.'),
(7, 'Parks & Greenery', 'Concerns related to the maintenance, cleanliness, or damage of parks, gardens, and green connectors.'),
(8, 'Smoking', 'Complaints regarding smoking in prohibited areas such as food premises, parks, or public spaces.'),
(9, 'Shared Bicycles', 'Issues related to improper parking, abandonment, or obstruction caused by shared bicycles.'),
(10, 'Abandoned Trolleys', 'Reports of supermarket trolleys abandoned in public areas and causing obstruction.'),
(11, 'Drains & Sewers', 'Problems involving blocked drains, sewage overflows, flooding, or drainage infrastructure damage.'),
(12, 'Construction Sites', 'Complaints about disturbances such as noise, dust, or safety hazards from construction activities.'),
(13, 'Drinking Water', 'Issues concerning water supply interruptions, leaks, water pressure, or water quality.'),
(14, 'Others', 'Reports that do not fit into predefined categories but still require municipal attention.')
ON CONFLICT (name) DO NOTHING;
