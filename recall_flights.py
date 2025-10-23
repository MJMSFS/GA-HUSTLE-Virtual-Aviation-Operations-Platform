import mysql.connector

# Function to recall logged flights
def recall_flights():
    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="msfs_database"
        )
        cursor = conn.cursor()

        # SQL query to fetch all flight logs
        query = "SELECT * FROM flights;"
        cursor.execute(query)

        # Fetch and display the results
        flights = cursor.fetchall()
        for flight in flights:
            print(f"Flight ID: {flight[0]}, Pilot ID: {flight[1]}, Aircraft Type: {flight[2]}, Aircraft Ident: {flight[3]}, Flight Number: {flight[4]}")
            print(f"Takeoffs (Day/Night): {flight[5]}/{flight[6]}, Landings (Day/Night): {flight[7]}/{flight[8]}, Instrument Approaches: {flight[9]}")
            print(f"Departure: {flight[10]}, Destination: {flight[11]}, Flight Date: {flight[12]}, Flight Hours: {flight[13]}")
            print("-" * 40)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Call the function
recall_flights()