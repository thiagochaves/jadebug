Nothing.class: Nothing.java
	javac Nothing.java
clean:
	rm -f *.class
run-debug: Nothing.class
	java -Xdebug -Xrunjdwp:transport=dt_socket,address=5005,server=y,suspend=y Nothing
run-debug-forever: Nothing.class
	bash -c "while true; do make run-debug; done"
mypy:
	rye run mypy -p jadebug
mypy-forever:
	watch --color rye run mypy -p jadebug
lint:
	rye run ruff check jadebug
lint-forever:
	watch --color rye run ruff check jadebug
test:
	rye run pytest
test-forever:
	watch --color rye run pytest --color=yes
.PHONY: clean run-debug run-debug-forever mypy mypy-forever lint lint-forever test test-forever
