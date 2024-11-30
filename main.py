from config import TOKEN, GROUPS_DATA
from publisher import publisher_image

def main():
    publisher_image(TOKEN, GROUPS_DATA)

if __name__ == "__main__":
    main()