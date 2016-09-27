from multiprocessing import Process


def processfunc(*args):
	print(args)


if __name__ == "__main__":
	pNum = 12
	jobs = list()

	for i in range(pNum):
		j = Process(target=processfunc,args="args")

		jobs.append(j)
		j.start()

	for j in jobs:
		j.join()