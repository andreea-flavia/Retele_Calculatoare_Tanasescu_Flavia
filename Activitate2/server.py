import socket

HOST        = '127.0.0.1'
PORT        = 9999
BUFFER_SIZE = 1024


clienti_conectati = {}
mesaje_publicate = {}
urmatorul_id = 1

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("=" * 50)
print(f"  SERVER UDP pornit pe {HOST}:{PORT}")
print("  Asteptam mesaje de la clienti...")
print("=" * 50)

while True:
    try:
        date_brute, adresa_client = server_socket.recvfrom(BUFFER_SIZE)
        mesaj_primit = date_brute.decode('utf-8').strip()

        parti = mesaj_primit.split(' ', 1)
        comanda = parti[0].upper()
        argumente = parti[1] if len(parti) > 1 else ''

        print(f"\n[PRIMIT] De la {adresa_client}: '{mesaj_primit}'")

        if comanda == 'CONNECT':
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat la server."
            else:
                clienti_conectati[adresa_client] = True
                nr_clienti = len(clienti_conectati)
                raspuns = f"OK: Conectat cu succes. Clienti activi: {nr_clienti}"
                print(f"[SERVER] Client nou conectat: {adresa_client}")

        elif comanda == 'DISCONNECT':
            if adresa_client in clienti_conectati:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Deconectat cu succes. La revedere!"
                print(f"[SERVER] Client deconectat: {adresa_client}")
            else:
                raspuns = "EROARE: Nu esti conectat la server."

        elif comanda == 'PUBLISH':
            # Verifica daca clientul este conectat
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Trebuie sa fii conectat pentru a publica mesaje."
            # Verifica ca mesajul nu este gol
            elif not argumente.strip():
                raspuns = "EROARE: Mesajul nu poate fi gol."
            else:
                mesaj_id = urmatorul_id
                mesaje_publicate[mesaj_id] = {
                    'client': adresa_client,
                    'mesaj': argumente.strip()
                }
                urmatorul_id += 1
                raspuns = f"OK: Mesaj publicat cu ID={mesaj_id}"

        elif comanda == 'DELETE':
            # Verifica daca clientul este conectat
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Trebuie sa fii conectat pentru a sterge mesaje."
            # Verifica ca argumentul este un numar intreg valid
            elif not argumente.strip().isdigit():
                raspuns = "EROARE: ID invalid. Trebuie sa fie un numar intreg."
            else:
                id_mesaj = int(argumente.strip())
                # Cauta mesajul cu ID-ul dat
                if id_mesaj not in mesaje_publicate:
                    raspuns = "EROARE: Nu exista niciun mesaj cu acest ID."
                # Verifica daca mesajul a fost publicat de clientul care face cererea
                elif mesaje_publicate[id_mesaj]['client'] != adresa_client:
                    raspuns = "EROARE: Doar autorul poate sterge propriul mesaj."
                else:
                    del mesaje_publicate[id_mesaj]
                    raspuns = f"OK: Mesajul cu ID={id_mesaj} a fost sters."

        elif comanda == 'LIST':
            # Verifica daca clientul este conectat
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Trebuie sa fii conectat pentru a vedea lista de mesaje."
            elif not mesaje_publicate:
                raspuns = "Nu exista mesaje publicate."
            else:
                lista = [f"{mid}: {info['mesaj']}" for mid, info in mesaje_publicate.items()]
                raspuns = "Mesaje publicate:\n" + "\n".join(lista)

        else:
            raspuns = f"EROARE: Comanda '{comanda}' este necunoscuta. Comenzi valide: CONNECT, DISCONNECT, PUBLISH, DELETE, LIST"

        server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
        print(f"[TRIMIS]  Catre {adresa_client}: '{raspuns}'")

    except KeyboardInterrupt:
        print("\n[SERVER] Oprire server...")
        break
    except Exception as e:
        print(f"[EROARE] {e}")

server_socket.close()
print("[SERVER] Socket inchis.")
