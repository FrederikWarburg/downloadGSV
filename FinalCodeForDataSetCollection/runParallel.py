from mainFunction import mainFunction
from multiprocessing import Pool, Process


cityNames = ['London', 'Boston', 'Los Angeles','Madrid']
#cityNames = ['London']


if __name__ == '__main__':
    with Pool(4) as p:
        p.map(mainFunction, cityNames)