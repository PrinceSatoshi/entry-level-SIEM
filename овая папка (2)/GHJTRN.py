from datetime import datetime

x = input("Название файла для скана:")
print("Открываю:", x)

events = []
with open(x, "r") as file:
    for line in file:
        parts = line.split()
        if len(parts) !=7:
            continue
        data, time, source, destination, protocol, port, event_type = parts
        port = int(port)
        timestamp = datetime.strptime(data + " " + time, "%Y-%m-%d %H:%M:%S")
        event = {
            "data": data,
            "time": time,
            "source": source,
            "destination": destination,
            "protocol": protocol,
            "port": port,
            "event_type": event_type,
            "timestamp": timestamp
        }
        events.append(event)
events.sort(key=lambda event: event["timestamp"])
for event in events:
    print(event["timestamp"])

max_counts={}
for event in events:
    count = 0
    for other_event in events:
        if event["source"] == other_event["source"]:
            difference = event["timestamp"] - other_event["timestamp"]
            if difference.total_seconds() >= 0 and difference.total_seconds() <= 60:
                count += 1
    print(event["timestamp"], event["source"], count)
    source = event["source"]
    if source not in max_counts:
        max_counts[source] = count
    elif count > max_counts[source]:
        max_counts[source] = count
print(max_counts)

services = {
    (22, "TCP"): "SSH",
    (80, "TCP"): "HTTP",
    (443, "TCP"): "HTTPS",
    (53, "UDP"): "DNS",
    (25, "TCP"): "SMTP",
    (110, "TCP"): "POP3",
    (143, "TCP"): "IMAP",
    (3389, "TCP"): "RDP",
    (445, "TCP"): "SMB"
}
for event in events:
    key = (event["port"], event["protocol"])
    service = services.get(key, "Unknown")
    event["service"] = service


connections = {}
destinations = {}
for event in events:
    source = event["source"]
    if source not in connections:
        connections[source] = 0
    connections[source] += 1
for event in events:
    source = event["source"]
    destination = event["destination"]
    if source not in destinations:
        destinations[source] = set()
    destinations[source].add(destination)



alerts = {}
points = 0
    #неизвестный
for event in events:
    source = event["source"]
    if source not in alerts:
        alerts[source] = []
    if event["service"] == "Unknown":
        alerts[source].append({
            "reason": "неизвестный прикладной протокол",
            "event1": event
            })
for source in max_counts:
    if source not in alerts:
        alerts[source] = []
    if max_counts[source] > 5:
        alerts[source].append({
            "reason": "высокая активность",
            "число": max_counts
        })
for source in destinations:
    if source not in alerts:
        alerts[source] = []
    if len(destinations[source]) > 3:
        alerts[source].append({
            "reason": "уникал. IP:",
            "destinations": destinations[source]
        })

risks = {}
for source in alerts:
    point = 0
    for reason in alerts[source]:
        if reason["reason"] == "высокая активность":
            point += 4
        if reason["reason"] == "неизвестный прикладной протокол":
            point += 3
        if reason["reason"] == "уникал. IP:":
            point += 3
    risks[source] = point

for source in alerts:
    print("╔══════════════════════════════════════╗")
    print(f"║  IP: {source}","                      ║")
    print("╠══════════════════════════════════════╣")
    for reason in alerts[source]:
        print("║ [!]", reason["reason"],)
        if "event1" in reason:
            event = reason["event1"]
            print("║ \033[36m[!]", event["data"], event["time"],"\033[0m")
            print("║ [!]",event["source"], "->", f'{event["destination"]}:{event["port"]} {event["protocol"]}')
        if "число" in reason:
            print("║ [!]","Событий:", reason["число"])
        if "destinations" in reason:
            for ips in reason["destinations"]:
                print("║ [!]","IP:", ips)
    if risks[source] > 7:
        print("║ \033[91m[!]","Уровень риска: высокий\033[0m"),
    elif risks[source] > 3:
        print("║ \033[33m[!]","Уровень риска: средний\033[0m")
    else:
        print("║ \033[92m[!]","Уровень риска: низкий\033[0m")
    print("╚══════════════════════════════════════╝")

input("Нажмите Enter, чтобы завершить работу")