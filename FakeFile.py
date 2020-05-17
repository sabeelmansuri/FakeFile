'''
This program simulates file operations using a FakeFile class and overriding the
reserved method open(). It is intended to be used on platforms where disk-
access is prohibited.
'''


from io import UnsupportedOperation


'''Overrides open() to return modified FakeFile object

Relies on two global variables being properly initialized:
    1) CONTENT (str) - fake file contents
    2) EXPECTED_FILES (list(str)) - expected names of files in directory
'''
def open(file_name, file_mode="r"):
    if file_name not in EXPECTED_FILES:
        raise FileNotFoundError("Errno 2] No such file or directory: '" + file_name + "'")
    return FakeFile(file_name, CONTENT, file_mode)


''' FakeFile class

Stores "file" as str
'''
class FakeFile:
    def __init__(self, file, content, file_mode):
        self.file_name = file
        self.content = "" if file_mode == "w" else content
        self.file_mode = file_mode
        self.file_pointer = 0
        self.closed = False
    
    def __iter__(self):
        return FakeFileIterator(self)

    def validate(func):
        def wrapper(self, *argv):
            if self.closed:
                raise ValueError("I/O operation on closed file.")
            return func(self, *argv)
        return wrapper

    @validate
    def readline(self):
        if "r" not in self.file_mode:
            raise UnsupportedOperation("not readable")
        try:
            line = self.content[self.file_pointer:].splitlines(keepends=True)[0]
            self.file_pointer += len(line)
        except IndexError:
            line = ""
        return line

    @validate
    def readlines(self):
        if "r" not in self.file_mode:
            raise UnsupportedOperation("not readable")
        lines = self.content[self.file_pointer:].splitlines(keepends=True)
        self.file_pointer += len(self.content)
        return lines

    @validate
    def write(self, text):
        if not ("w" in self.file_mode or "a" in self.file_mode):
            raise UnsupportedOperation("not writable")
        self.content += text
        self.file_pointer += len(text)
        
    @validate
    def writelines(self, texts):
        if not ("w" in self.file_mode or "a" in self.file_mode):
            raise UnsupportedOperation("not writable")
        text = ''.join(texts)
        self.content += text
        self.file_pointer += len(text)

    def close(self):
        self.closed = True

    def name(self):
        return self.file_name

    def mode(self):
        return self.file_mode

    
''' FakeFile iterator class

Enables looping over FakeFile objects
'''
class FakeFileIterator:
    def __init__(self, fakefile):
        self.fakefile = fakefile

    def __next__(self):
        if self.fakefile.file_pointer < len(self.fakefile.content):
            end =  self.fakefile.content.find("\n", self.fakefile.file_pointer)
            if end == -1:
                nxt = self.fakefile.content[self.fakefile.file_pointer:]
            else:
                nxt = self.fakefile.content[self.fakefile.file_pointer : end + 1]
            self.fakefile.file_pointer += len(nxt)
            return nxt
        raise StopIteration

CONTENT = ""
EXPECTED_FILES = [""]