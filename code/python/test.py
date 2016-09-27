from multiprocessing import Process


def test(*tt):
	print type(tt)
	print(len(tt))
	print(tt[0])
	print(tt[1])
	print(tt[2])


if __name__ == "__main__":
	tt = "test"
	l = list()
	l.append("abc")
	j = Process(target=test,args=(tt,"abc",l))
	j.start()
	j.join()