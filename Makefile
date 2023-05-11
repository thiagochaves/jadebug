Nothing.class: Nothing.java
	javac Nothing.java
clean:
	rm -f *.class
run-debug: Nothing.class
	java -Xdebug -Xrunjdwp:transport=dt_socket,address=5005,server=y,suspend=y Nothing
run-debug-forever: Nothing.class
	bash -c "while true; do make run-debug; done"
check-types:
	watch rye run mypy -p jadebug
lint:
	watch rye run ruff check jadebug
test:
	watch rye run pytest
.PHONY: clean run-debug run-debug-forever check-types lint test
