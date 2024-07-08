#!/usr/bin/env python3

"""
🔒 This script is used to encrypt values files using sops with age. 🔒

It takes a directory as an argument, finds all `values.*.yaml` files in the directory,
excluding `values.enc.yaml`, and encrypts them using `sops` with age, fetching the age public key
from an optional argument or an environment variable.

Usage:
    python3 script.py [directory] [--age-key AGE_KEY]
    or
    AGE_KEY=your_age_public_key python3 script.py [directory]
"""

import os
import argparse
import subprocess
from pathlib import Path
from termcolor import colored

class ValuesEncryptor:
    """
    🔐 This class is responsible for encrypting values files. 🔐
    """

    def __init__(self, path, age_key):
        """
        Initialize the ValuesEncryptor with a directory path and age public key.

        Args:
            path (str): The directory path.
            age_key (str): The age public key.
        """
        self.path = path
        self.age_key = age_key
        self.encrypted_files = 0

    def encrypt_file(self, file_path):
        """
        This method encrypts a single file using `sops` with age.

        Args:
            file_path (str): The path to the file to be encrypted.
        """
        print(colored(f"🔐 Encrypting {file_path}", 'green'))
        process = subprocess.Popen(['sops', '--encrypt', '--age', self.age_key, file_path], stdout=subprocess.PIPE)
        encrypted_content, err = process.communicate()

        encrypted_file_path = file_path.replace('.yaml', '.enc.yaml')
        with open(encrypted_file_path, 'wb') as f:
            f.write(encrypted_content)
        self.encrypted_files += 1

    def encrypt_values(self, path=None):
        """
        This method encrypts all matching values files in a directory. It traverses the directory recursively
        and calls `encrypt_file` on each matching file.

        Args:
            path (str, optional): The directory path. Defaults to None.

        Returns:
            int: The number of encrypted files.
        """
        if path is None:
            path = self.path

        if os.path.isfile(path) and path.endswith('.yaml') and 'values.' in path and not path.endswith('values.enc.yaml'):
            self.encrypt_file(path)
        elif os.path.isdir(path):
            for child in os.listdir(path):
                self.encrypt_values(os.path.join(path, child))

        return self.encrypted_files

def main():
    """
    The main function of the script. It handles the command-line arguments and
    the traversal of the directory.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description='Encrypt values files using sops with age')
    parser.add_argument('dir', type=str, help='Directory to find values files')
    parser.add_argument('--age-key', type=str, default=os.environ.get('AGE_KEY'), help='Age public key for encryption')
    args = parser.parse_args()

    if not args.age_key:
        print(colored("Error: Age public key must be provided via --age-key argument or AGE_KEY environment variable.", 'red'))
        exit(1)

    if os.path.isdir(args.dir):
        print(colored(f"🔍 Checking files in {args.dir}", 'blue'))
        encryptor = ValuesEncryptor(args.dir, args.age_key)
        encrypted_files = encryptor.encrypt_values()
        print(colored(f"🎉 Encryption complete. {encrypted_files} files encrypted.", 'green'))

if __name__ == "__main__":
    main()