## How to work with dockerized environment

First you have to build the docker image:

```
docker build -t web-crawl-stats .
```

Run the app

```
docker run web-crawl-stats
```

## Description of the problem

The goal of this is to parse and extract different statistics from the robots.txt files.
We will use the data from the CommonCrawl project ([https://commoncrawl.org/](https://commoncrawl.org/)).
CommonCrawl is a project that crawls the web and stores the data in a public S3 bucket using WARC format ([https://en.wikipedia.org/wiki/Web_ARChive](https://en.wikipedia.org/wiki/Web_ARChive)).

The robots.txt ([https://en.wikipedia.org/wiki/Robots_exclusion_standard](https://en.wikipedia.org/wiki/Robots_exclusion_standard)) is a file that is used by web crawlers to identify which parts of the website should not be crawled. The file is located in the root of the website and it is expected to be in the following format:

```
User-agent: Googlebot
Disallow: /images
```

The output data file will be in the `data/statistics/` directory.
