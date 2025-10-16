module.tar.gz:
	tar czf $@ *.sh .env src requirements.txt meta.json

clean:
	rm -f module.tar.gz
	rm -rf .venv

.PHONY: clean
