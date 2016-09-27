package main

import (
	"fmt"
)

func gen(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		for _, n := range nums {
			out <- n
		}
		close(out)
	}()
	return out
}

func sq(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		for n := range in {
			out <- n * n
		}
		close(out)
	}()
	return out
}

func consumer(in <-chan int) {
	for n := range in {
		fmt.Println(n)
	}
}

func main() {
	//set up the pipeline
	c := gen(2, 3)
	out := sq(c)
	//consume the output
	consumer(out)
}
