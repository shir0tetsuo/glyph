import os

def read_file_as_list(file_path):
    '''Returns list of lines from file (UTF-8).'''
    with open(file_path, 'r', encoding='UTF-8') as file:
        return [line.strip() for line in file]

class SavedMaps:

    def __init__(self, path=os.getcwd()):

        self.path = os.path.join(path, 'heightmaps')

        self.items = [item for item in next(os.walk(self.path))[2]]

        pass
    
    def read_file_as_string(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            return f"Error: The file at {file_path} was not found."
        except Exception as e:
            return f"Error: {e}"
    
    @property
    def maps(self):
        return {item:self.read_file_as_string(os.path.join(self.path, item)) for item in self.items}


class SavedColors:

    def __init__(self, path=os.getcwd()):

        self.path = os.path.join(path, 'colors')

        self.items = [item for item in next(os.walk(self.path))[2]]

        pass

    @property
    def maps(self):
        return {item:read_file_as_list(os.path.join(self.path, item)) for item in self.items}

class SavedGlyphs:

    def __init__(self, path=os.getcwd(), fontdir='/usr/share/fonts/truetype/noto/'):

        self.path = os.path.join(path, 'glyphtables')

        self.fontdir = fontdir

        self.items = [item for item in next(os.walk(self.path))[2]]

        pass

    @property
    def maps(self):
        return {
            os.path.splitext(filename)[0]: [
                filedata[1],  # Glyphs
                os.path.join(self.fontdir, filedata[0])  # Directory
            ]
            for filename in self.items
            for filedata in [read_file_as_list(os.path.join(self.path, filename))]
        }