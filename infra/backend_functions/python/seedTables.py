# Python
import psycopg2

connection = psycopg2.connect(
    user='postgres',
    password='fyukiAmane03!',
    host='localhost',
    port='5432',
    database='municipal_app'
)

seed_statements = [
    """
    INSERT INTO town_councils (council_name) VALUES
        ('Ang Mo Kio Town Council'),
        ('Bishan-Toa Payoh Town Council'),
        ('Chua Chu Kang Town Council'),
        ('Holland-Bukit Panjang Town Council'),
        ('Jalan Besar Town Council'),
        ('Jurong-Clementi Town Council'),
        ('Marine Parade Town Council'),
        ('Marsiling-Yew Tee Town Council'),
        ('Nee Soon Town Council'),
        ('Pasir Ris-Punggol Town Council'),
        ('Sembawang Town Council'),
        ('Sengkang Town Council'),
        ('Tampines Town Council'),
        ('Tanjong Pagar Town Council'),
        ('West Coast Town Council'),
        ('Aljunied-Hougang Town Council'),
        ('East Coast Town Council');
    """,
    """
    INSERT INTO issue_types (name) VALUES
        ('Pests'),
        ('Animals & Bird'),
        ('Smoking'),
        ('Parks & Greenery'),
        ('Drains & Sewers'),
        ('Drinking Water'),
        ('Construction Sites'),
        ('Abandoned Trolleys'),
        ('Shared Bicycles'),
        ('Others');
    """,
    """
    INSERT INTO issue_subcategories (issue_type_id, name) VALUES
        (1, 'Cockroaches in Food Establishment'),
        (1, 'Mosquitoes'),
        (1, 'Rodents in Common Areas'),
        (1, 'Rodents in Food Establishment'),
        (1, 'Bees & Hornets'),
        (2, 'Dead Animal'),
        (2, 'Injured Animal'),
        (2, 'Bird Issues'),
        (2, 'Cat Issues'),
        (2, 'Dog Issues'),
        (2, 'Other Animal Issues'),
        (3, 'Food Premises'),
        (3, 'Parks & Park Connectors'),
        (3, 'Other Public Areas'),
        (4, 'Fallen Tree/Branch'),
        (4, 'Overgrown Grass'),
        (4, 'Park Lighting Maintenance'),
        (4, 'Park Facilities Maintenance'),
        (4, 'Other Parks and Greenery Issues'),
        (5, 'Choked Drain/Stagnant Water'),
        (5, 'Damaged Drain'),
        (5, 'Flooding'),
        (5, 'Sewer Choke/Overflow'),
        (5, 'Sewage Smell'),
        (6, 'No Water'),
        (6, 'Water Leak'),
        (6, 'Water Pressure'),
        (6, 'Water Quality'),
        (7, 'Construction Noise'),
        (8, 'Cold Storage'),
        (8, 'Giant'),
        (8, 'Mustafa'),
        (8, 'FairPrice'),
        (8, 'ShengSong'),
        (8, 'Ikea'),
        (9, 'Anywheel'),
        (9, 'HelloRide'),
        (9, 'Others'),
        (10, 'Others');
    """,
    """
    INSERT INTO agencies (agency_name) VALUES
        ('Building and Construction Authority (BCA)'),
        ('Housing & Development Board (HDB)'),
        ('Land Transport Authority (LTA)'),
        ('National Environment Agency (NEA)'),
        ('National Parks Board (NParks)'),
        ('People’s Association (PA)'),
        ('Public Utilities Board (PUB)'),
        ('Singapore Land Authority (SLA)'),
        ('Singapore Police Force (SPF)'),
        ('Urban Redevelopment Authority (URA)');
    """
]

try:
    with connection:
        with connection.cursor() as cursor:
            for stmt in seed_statements:
                cursor.execute(stmt)
    print("Seed data inserted successfully.")
except Exception as e:
    print("Error:", e)
finally:
    connection.close()