# TCP-client stress test voor een Pi server
# Geschreven door: Nina Schrauwen
import socket
import time
import statistics

# Configureer de host en poort van de Pi server
HOST = '192.168.2.30'  # or Pi's IP
PORT = 5000

def test_for_duration(s, payload, duration_sec=30):
    rtts = []
    # Eindtijd is de huidige tijd plus de duur in seconden
    end_time = time.perf_counter() + duration_sec
    count = 0
    # Verstuur de payload en ontvang de response zolang de tijd nog niet is verstreken
    while time.perf_counter() < end_time:
        start = time.perf_counter()
        s.sendall(payload)
        data = s.recv(1024)
        stop = time.perf_counter()

        # Check of de response begint met 'pong'
        if not data.startswith(b'pong'):
            print("Unexpected response:", data)
            return False, None

        # Bereken de round-trip time (RTT) per ping en voeg de RTT toe aan de lijst
        rtts.append((stop - start) * 1000)  # ms
        count += 1

    # Avg. RTT bereken je door de som van alle RTT's te delen door het aantal RTT's
    avg_rtt = sum(rtts) / len(rtts)
    # Max. RTT is de grootste RTT in de lijst
    max_rtt = max(rtts)
    # Jitter is de standaarddeviatie van de RTT's (hoeveel de RTT's variëren van de gemiddelde RTT)
    jitter = statistics.stdev(rtts) if len(rtts) > 1 else 0
    # Throughput is het aantal pings gedeeld door de duur in seconden
    throughput = count / duration_sec

    # Stop de statistieken in een dictionary
    metrics = {
        'count': count,
        'avg_rtt': avg_rtt,
        'max_rtt': max_rtt,
        'jitter': jitter,
        'throughput': throughput,
        'payload_size': len(payload)
    }
    return True, metrics

# Start de test met een payload van 512 bytes (later verdubbeld)
payload = b'a' * 512
# Duur van de test in seconden, om de server te stressen (maar niet oneindig)
duration_sec = 30

# Open een socket verbinding met de Pi server via de opgegeven host en poort
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # Korte delay om haperingen te voorkomen bij het uitvoeren van de test
    s.settimeout(1.0)

    while True:
        try:
            # Roep de test functie om de server te pingen met de payload
            ok, metrics = test_for_duration(s, payload, duration_sec)

            # Als je een False terugkrijgt, dan is er iets misgegaan (stop de test)
            if not ok:
                print("Unexpected response — stopping.")
                break

            # Print de resultaten van de test wanneer de test succesvol was (ok is True)
            print(
                f"Payload {metrics['payload_size']} bytes | "
                f"{metrics['count']} pings in {duration_sec}s | "
                f"avg RTT: {metrics['avg_rtt']:.3f} ms | "
                f"max RTT: {metrics['max_rtt']:.3f} ms | "
                f"jitter: {metrics['jitter']:.3f} ms | "
                f"throughput: {metrics['throughput']:.1f} pings/sec"
            )

            # Als de avg. RTT boven de 100 ms is of de throughput onder de 10 pings/sec ligt, stop dan de test en print een waarschuwing
            if metrics['avg_rtt'] > 100 or metrics['throughput'] < 10:
                print("Performance degraded — stopping.")
                break

            # Wanneer de vorige payload succesvol was, verdubbel de payload voor de volgende ronde
            payload *= 2  # double the payload each round

        # Wanneer er een timeout is, print een bericht en stop de test
        except socket.timeout:
            print("Timeout — server not responding.")
            break
        # Wanneer er een socket error is, print een bericht en stop de test
        except socket.error as e:
            print(f"Socket error: {e}")
            break
            
