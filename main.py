import requests
import time
import threading

def get_proxies_from_file(filename):
    proxies = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if line:
                proxies.append(line)
                print(f"Added proxy: {line}")
    return proxies

def get_uuids(usernames, proxy):
    url = "https://api.mojang.com/profiles/minecraft"
    headers = {"Content-Type": "application/json"}
    uuids = []

    proxies_dict = {
        "http": proxy,
        "https": proxy
    }

    try:
        response = requests.post(url, headers=headers, json=usernames, proxies=proxies_dict, timeout=12)
        response.raise_for_status()
        uuids = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Proxy {proxy} failed: {e}")

    return uuids

def write_uuids_to_file(uuids_filename, uuids):
    with open(uuids_filename, "a") as file:
        for profile in uuids:
            file.write(f"{profile['id']}:{profile['name']}\n")
    print(f"UUIDs and usernames written to {uuids_filename}")

def process_usernames_batch(usernames_batch, proxy):
    try:
        uuids = get_uuids(usernames_batch, proxy)
        if uuids:
            print("UUIDs for the provided usernames:")
            for profile in uuids:
                print(f"Username: {profile['name']}, UUID: {profile['id']}")
            write_uuids_to_file("gathered_uuids.txt", uuids)
        else:
            print("No valid Minecraft profiles found.")
    except Exception as e:
        print(f"Error getting UUIDs: {e}")

def main():
    proxies = get_proxies_from_file("proxy.txt")

    while True:
        try:
            num_threads = int(input("Enter the number of threads (1-100) to use for processing (reccomended use less than num of proxies): "))
            if not (1 <= num_threads <= 100):
                raise ValueError("Number of threads must be between 1 and 10.")
            break
        except ValueError as ve:
            print(f"Error: {ve}")

    while True:
        option = input("Choose an option:\n1. Get UUIDs from usernames\n2. (OUTDATED)Get name history from UUID(OUTDATED)\nEnter option (1 or 2): ")

        if option == "1":
            source_option = input("Choose source:\n1. Enter usernames manually\n2. Read usernames from file\nEnter source (1 or 2): ")

            if source_option == "1":
                usernames = input("Enter usernames separated by commas: ").split(',')
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

            # Process usernames in batches using multiple threads
            batch_size = num_threads * 10  # Each thread processes 10 usernames
            while usernames:
                if len(usernames) >= batch_size:
                    # Take up to batch_size usernames for the current batch
                    batch_usernames = usernames[:batch_size]
                    usernames = usernames[batch_size:]
                else:
                    # Take all remaining usernames if fewer than batch_size left
                    batch_usernames = usernames
                    usernames = []

                # Create and start threads for processing the current batch
                threads = []
                for i in range(num_threads):
                    start_idx = i * 10
                    end_idx = start_idx + 10
                    if proxies:
                        proxy = proxies[i % len(proxies)]  # Cycle through proxies
                        thread = threading.Thread(target=process_usernames_batch, args=(batch_usernames[start_idx:end_idx], proxy))
                        threads.append(thread)
                        thread.start()

                # Wait for all threads to complete before processing the next batch
                for thread in threads:
                    thread.join()

        elif option == "2":
            # Implement option 2 (get name history from UUID) if needed
            print("Option 2 is not implemented anymore")
        else:
            print("Invalid option. Please enter 1 or 2.")

        # Prompt to exit the program
        print("SUCCESSFULLY FOUND ALL INPUTTED UUIDs")
        quit_choice = input("Do you want to quit? (y/n): ")
        if quit_choice.lower() == "y":
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
