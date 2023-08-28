clean:
	rm -f dist/*
	rm src/slambda/data/playground.frontend

clean-dist:
	rm -f dist/*

playground:
	utils/build_frontend.sh

package:
	utils/package.sh

upload:
	utils/upload.sh
