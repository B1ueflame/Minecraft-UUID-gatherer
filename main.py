import requests
import time

def get_proxies_from_file(filename):
    proxies = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                proxies.append(line)
                print(f"Added proxy: {line}")
    return proxies

def get_uuids(usernames, proxies):
    url = "https://api.mojang.com/profiles/minecraft"
    headers = {"Content-Type": "application/json"}
    uuids = []

    for proxy in proxies:
        proxies_dict = {
            "http": proxy,
            "https": proxy
        }

        try:
            response = requests.post(url, headers=headers, json=usernames, proxies=proxies_dict, timeout=12)
            response.raise_for_status()
            uuids = response.json()
            break  #Break out of loop if request succeeds
        except requests.exceptions.RequestException as e:
            print(f"Proxy {proxy} failed: {e}")
            time.sleep(1)  #Wait for a short time before retrying with the next proxy

    return uuids

def write_uuids_to_file(uuids_filename, uuids):
    with open(uuids_filename, "a") as file:  #Append mode to add to the existing file
        for profile in uuids:
            file.write(f"{profile['id']}:{profile['name']}\n")
    print(f"UUIDs and usernames written to {uuids_filename}")

def main():
    proxies = get_proxies_from_file("proxy.txt")

    while True:
        option = input("Choose an option:\n1. Get UUIDs from usernames\n2. (OUTDATED)Get name history from UUID(OUTDATED)\nEnter option (1 or 2): ")

        if option == "1":
            source_option = input("Choose source:\n1. Enter usernames manually\n2. Read usernames from file\nEnter source (1 or 2): ")

            if source_option == "1":
                usernames = input("Enter up to 10 usernames separated by commas: ").split(',')
                usernames = [username.strip() for username in usernames]
            elif source_option == "2":
                usernames = []
                with open("names.txt", "r") as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            usernames.append(line)

            if not usernames:
                print("No usernames provided.")
                continue

            while usernames:
                #Take up to 10 usernames for the current batch
                batch_usernames = usernames[:10]
                usernames = usernames[10:]

                try:
                    uuids = get_uuids(batch_usernames, proxies)
                    if uuids:
                        print("UUIDs for the provided usernames:")
                        for profile in uuids:
                            print(f"Username: {profile['name']}, UUID: {profile['id']}")
                        #Append UUIDs to file
                        write_uuids_to_file("gathered_uuids.txt", uuids)
                    else:
                        print("No valid Minecraft profiles found.")
                except Exception as e:
                    print(f"Error getting UUIDs: {e}")

            #Check if there are any remaining usernames after processing batches
            if usernames:
                try:
                    uuids = get_uuids(usernames, proxies)
                    if uuids:
                        print("UUIDs for the remaining usernames:")
                        for profile in uuids:
                            print(f"Username: {profile['name']}, UUID: {profile['id']}")
                        # Append UUIDs to file
                        write_uuids_to_file("gathered_uuids.txt", uuids)
                    else:
                        print("No valid Minecraft profiles found for remaining usernames.")
                except Exception as e:
                    print(f"Error getting UUIDs for remaining usernames: {e}")

        elif option == "2":
            #Implement option 2 (get name history from UUID) if needed
            print("Option 2 is not implemented anymore")
        else:
            print("Invalid option. Please enter 1 or 2.")
        print("SUCCESSFULLY FOUND ALL INPUTTED UUIDs")
        quit = input("Do you want to quit? (y/n): ")
        if quit.lower() == "y":
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
