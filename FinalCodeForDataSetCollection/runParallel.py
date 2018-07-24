from mainFunction import mainFunction
from multiprocessing import Pool, Process


#cityNames = ['San Francisco', 'London', 'Barcelona','Boston']
#cityNames = ['London', 'Madrid', 'San Francisco','Boston']
cityNames = ['Rio de Janeiro', 'Sydney', 'Tokyo','Mexico City']
#cityNames = ['London']


if __name__ == '__main__':
    with Pool(4) as p:
        p.map(mainFunction, cityNames)
