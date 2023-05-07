Nothing.class: Nothing.java
	javac Nothing.java
clean:
	rm -f *.class
run-debug: Nothing.class
	java -Xdebug -Xrunjdwp:transport=dt_socket,address=5005,server=y,suspend=y Nothing
run-debug-forever: Nothing.class
	bash -c "while true; do make run-debug; done"
.PHONY: clean run-debug run-debug-forever
