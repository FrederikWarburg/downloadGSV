import os

baseDirectory =  '/Users/frederikwarburg/Desktop/Zaragoza/dataset/London13/'

images = []

for folderName in os.listdir(baseDirectory):

    print(folderName)

    for file in os.listdir(baseDirectory +"/" + folderName + "/images"):

        images.append(file)