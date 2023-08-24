clean:
	rm -f dist/*
	rm src/slambda/data/playground.frontend

playground:
	utils/build_frontend.sh

package:
	utils/package.sh

upload:
	utils/upload.sh
