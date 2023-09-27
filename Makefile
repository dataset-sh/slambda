clean:
	rm -f dist/*

package:
	utils/package.sh

upload:
	utils/upload.sh
