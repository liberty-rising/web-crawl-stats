
run: build
	docker run web-crawl-stats


build:
	docker build -t web-crawl-stats .


