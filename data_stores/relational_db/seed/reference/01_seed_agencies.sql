INSERT INTO agencies (agency_id, name, description) VALUES
(1, 'Building and Construction Authority (BCA)', 'Regulates Singapore’s building and construction industry to ensure safety, sustainability, and quality standards.'),
(2, 'Housing & Development Board (HDB)', 'Provides affordable public housing and develops vibrant, sustainable towns for Singaporeans.'),
(3, 'Land Transport Authority (LTA)', 'Plans, designs, builds, and maintains Singapore’s land transport infrastructure and systems.'),
(4, 'National Environment Agency (NEA)', 'Protects Singapore’s environment through pollution control, public cleanliness, and environmental sustainability initiatives.'),
(5, 'National Parks Board (NParks)', 'Manages parks, gardens, and nature reserves, and oversees greenery and biodiversity conservation in Singapore.'),
(6, 'People’s Association (PA)', 'Fosters community bonding and social cohesion through grassroots and outreach programs.'),
(7, 'Public Utilities Board (PUB)', 'Manages Singapore’s water supply, water catchment, and drainage systems to ensure a sustainable water future.'),
(8, 'Singapore Land Authority (SLA)', 'Optimises land resources for Singapore’s social and economic development, and maintains the national land database.'),
(9, 'Singapore Police Force (SPF)', 'Maintains law and order, prevents crime, and ensures the safety and security of Singapore.'),
(10, 'Urban Redevelopment Authority (URA)', 'Plans and facilitates Singapore’s physical development to create a liveable and sustainable urban environment.')
ON CONFLICT (name) DO NOTHING;
