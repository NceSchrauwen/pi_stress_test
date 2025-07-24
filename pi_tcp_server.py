# TCP-server stress test voor een Pi server
# Geschreven door: Nina Schrauwen
import socket

# Luister op alle interfaces en poort 5000
HOST = ''
PORT = 5000

# Open een socket verbinding en luister naar inkomende verbindingen
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        # Verbind en luister bij de inkomende host via de opgegeven poort
        s.bind((HOST, PORT))
        s.listen()
        print(f"Listening on port {PORT}...")
        
        # Accepteer een inkomende verbinding
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            # Wanneer een verbinding is gemaakt, blijf data ontvangen (alle data accepteren)
            while True:
                data = conn.recv(1024)
                # Als er geen data is ontvangen, breek de loop
                if not data:
                    break
                # Stuur een 'pong' terug als antwoord
                conn.sendall(b'pong')
                
    # Als er een timeout optreedt, geef een foutmelding
    except TimeoutError:
        print("Connection timed out.")
        
    # Als er een andere fout optreedt, geef een foutmelding
    except Exception as e:
        print(f"An error occurred: {e}")
