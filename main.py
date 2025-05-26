import filesave

test = filesave.FileSaveSystem('test.txt', 'read-write', encoded=False, override=True)
print(test)
test.save()