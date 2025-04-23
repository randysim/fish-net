from fishing import create_fishing_client

if __name__ == "__main__":
    fishing_client = create_fishing_client(config_path="resource/config.json")
    fishing_client.run()