clean:
	rm -f dist/*

clean-dist:
	rm -f dist/*

package:
	utils/package.sh

upload:
	utils/upload.sh
