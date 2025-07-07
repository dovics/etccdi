import os
import zipfile


class ZipTarget:
    def __init__(self):
        self.files_to_add = []

    def add_folder(self, folder_path):
        """ 添加整个文件夹中的文件 """
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder {folder_path} does not exist.")

        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.files_to_add.append((file_path, os.path.relpath(file_path, os.getcwd())))

    def add_file(self, file_path):
        """ 添加单个文件 """
        if not os.path.isfile(file_path):
            raise ValueError(f"File {file_path} does not exist.")

        self.files_to_add.append((file_path, os.path.relpath(file_path, os.getcwd())))

    def save(self, zip_path):
        """ 保存所有添加的文件到 ZIP 包 """
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path, arcname in self.files_to_add:
                zipf.write(file_path, arcname)

        print(f"ZIP file saved at: {zip_path}")