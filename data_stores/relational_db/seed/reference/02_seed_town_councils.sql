DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM town_councils LIMIT 1) THEN
    INSERT INTO town_councils (town_council_id, name, description) VALUES
    (1, 'Ang Mo Kio Town Council', 'Manages and maintains the common property of residential blocks in Ang Mo Kio and parts of Kebun Baru and Yio Chu Kang.'),
    (2, 'Bishan-Toa Payoh Town Council', 'Oversees the maintenance of common areas in Bishan, Toa Payoh, and parts of Thomson and Marymount.'),
    (3, 'Chua Chu Kang Town Council', 'Administers estate services and property maintenance in Chua Chu Kang, Bukit Gombak, and Hong Kah North.'),
    (4, 'Holland-Bukit Panjang Town Council', 'Maintains residential areas in Holland-Bukit Timah and Bukit Panjang constituencies.'),
    (5, 'Jalan Besar Town Council', 'Manages the town council services for estates in Jalan Besar, Kolam Ayer, and Whampoa.'),
    (6, 'Jurong-Clementi Town Council', 'Oversees estates in Jurong GRC and Clementi, managing common properties and municipal services.'),
    (7, 'Marine Parade Town Council', 'Covers Marine Parade, Geylang Serai, and parts of Joo Chiat, overseeing estate management and town upkeep.'),
    (8, 'Marsiling-Yew Tee Town Council', 'Manages residential and communal spaces in Marsiling, Woodgrove, and Yew Tee areas.'),
    (9, 'Nee Soon Town Council', 'Responsible for the maintenance and management of Nee Soon Central, Nee Soon East, and Nee Soon South.'),
    (10, 'Pasir Ris-Punggol Town Council', 'Handles estate services and maintenance in Pasir Ris and Punggol areas.'),
    (11, 'Sembawang Town Council', 'Administers common property management for residential estates in Sembawang and Canberra.'),
    (12, 'Sengkang Town Council', 'Maintains and manages estates in Sengkang GRC, covering Anchorvale, Compassvale, Rivervale, and Buangkok.'),
    (13, 'Tampines Town Council', 'Oversees property maintenance and estate management in the Tampines area.'),
    (14, 'Tanjong Pagar Town Council', 'Manages public housing estates in Tanjong Pagar, Queenstown, and parts of Bukit Merah.'),
    (15, 'West Coast Town Council', 'Handles estate services in West Coast, Ayer Rajah-Gek Poh, Boon Lay, and Pioneer areas.'),
    (16, 'Aljunied-Hougang Town Council', 'Manages estates under Aljunied GRC and Hougang Single Member Constituency, overseeing maintenance and town improvement.'),
    (17, 'East Coast Town Council', 'Administers town management services for residents of East Coast GRC, including Bedok and parts of Siglap.')
    ON CONFLICT (name) DO NOTHING;
  END IF;
END
$$;