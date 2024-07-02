import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.database = psycopg2.connect(
            host = "localhost",
            database = "postgres",
            user="postgres",
            password = "postgres"
            )
    
    def get_order_information(self, order_id):
        cur = self.database.cursor()
        cur.execute(f"SELECT * FROM orders WHERE order_id = {order_id}")
        rows = cur.fetchall()
        cur.close()
        if len(rows) == 0:
            return "Sorry, that order doesn't exist. Please provide a valid order ID."
        return rows[0]
    

