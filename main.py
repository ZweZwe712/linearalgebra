from hill import text_cipher, image_cipher, audio_cipher

def main():
    print("="*40)
    print("   Hill Cipher Project - Multi Mode")
    print("="*40)
    print("Choose an option:")
    print("1. Text Mode")
    print("2. Image Mode")
    print("3. Audio Mode")
    print("0. Exit")

    choice = input("Enter choice: ")

    if choice == "1":
        text_cipher.run()
    elif choice == "2":
        print("\nImage Mode:")
        print("a. Encode")
        print("b. Decode")
        img_choice = input("Enter choice (a/b): ")
        if img_choice.lower() == "a":
            image_cipher.run(mode="encode")
        elif img_choice.lower() == "b":
            image_cipher.run(mode="decode")
        else:
            print("Invalid choice for image mode.")
    elif choice == "3":
        audio_cipher.run()
    elif choice == "0":
        print("Goodbye!")
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
    